"""Offline only. Fixture pins prove structure, never image availability or deployability."""
import argparse,collections,hashlib,json,re,subprocess,tempfile,tarfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'aws/review'
EXPECTED={'kubernetes.io/hostname':'capstone2-worker','capstone-workload':'robot-shop'}
TOL={'key':'capstone-workload','operator':'Equal','value':'robot-shop','effect':'NoSchedule'}
SHA='af35d3e93750ce46d90cbb6537483c8fa914f19fbffa19fbabcb2825181a0f1a'
def placed(s):return all(s.get('nodeSelector',{}).get(k)==v for k,v in EXPECTED.items()) and TOL in s.get('tolerations',[]) and not s.get('nodeName')
def quantity(v,memory=False):
 v=str(v)
 for suffix,factor in ([('Gi',1024),('Mi',1),('Ki',1/1024)] if memory else [('m',1)]):
  if v.endswith(suffix):return float(v[:-len(suffix)])*factor
 return float(v)/(1024**2) if memory else float(v)*1000

def main():
 p=argparse.ArgumentParser();p.add_argument('--helm',default='helm');p.add_argument('--monitoring-chart',required=True);p.add_argument('--output',default=str(OUT));p.add_argument('--test-admission-hooks',action='store_true');p.add_argument('--require-real-images',action='store_true');a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 chart=Path(a.monitoring_chart);assert hashlib.sha256(chart.read_bytes()).hexdigest()==SHA,'Chart package mismatch'
 errors=[];images=[];workloads=[];scoped=[];totals=[0.,0.,0.,0.];services=[];objects=[]
 names='web catalogue cart payment user shipping ratings dispatch mongodb mysql rabbitmq redis loadgen'.split()
 app_values=yaml.safe_load((ROOT/'aws/robot-shop.values.yaml').read_text())
 if a.require_real_images:
  assert all(re.fullmatch(r'[a-z0-9./:_-]+@sha256:[a-f0-9]{64}',app_values['images'].get(n,'')) for n in names),'Real immutable application images incomplete'
 fixtures={'images':{n:'example.invalid/structure-only/'+n+'@sha256:'+'a'*64 for n in names if not app_values['images'].get(n)},'loadgen':{'enabled':True}}
 aux_values=yaml.safe_load((ROOT/'aws/observability.values.yaml').read_text())
 aux={'components':{n:{'digest':'sha256:'+'a'*64} for n in ['blackbox','loki','otel','jaeger'] if not aux_values['components'][n]['digest']}}
 if not aux_values['fluentbit']['digest']:aux['fluentbit']={'digest':'sha256:'+'a'*64}
 with tempfile.TemporaryDirectory() as tmp:
  for label,chartpath,ns,values,fixture in [('robot-shop',ROOT/'robot-shop','robot-shop','robot-shop',fixtures),('monitoring',chart,'observability','monitoring',{'prometheusOperator':{'admissionWebhooks':{'enabled':True}}} if a.test_admission_hooks else {}),('capstone-observability',ROOT/'observability','observability','observability',aux)]:
   f=Path(tmp)/(label+'.yaml');f.write_text(yaml.safe_dump(fixture))
   cmd=[a.helm,'template',label,str(chartpath),'-n',ns,'-f',str(ROOT/'aws'/f'{values}.values.yaml'),'-f',str(f)]
   result=subprocess.run(cmd,capture_output=True,text=True);assert result.returncode==0,result.stderr
   docs=[d for d in yaml.safe_load_all(result.stdout) if d]
   for o in docs:
    kind=o['kind'];name=o['metadata']['name'];namespace=o['metadata'].get('namespace',ns);spec=o.get('spec',{})
    objects.append({'release':label,'kind':kind,'name':name,'namespace':None if kind in ['ClusterRole','ClusterRoleBinding','CustomResourceDefinition','MutatingWebhookConfiguration','ValidatingWebhookConfiguration'] else namespace})
    if namespace not in ['robot-shop','observability']:errors.append(f'Namespace escape {kind}/{name}')
    if kind in ['ClusterRole','ClusterRoleBinding','MutatingWebhookConfiguration','ValidatingWebhookConfiguration','CustomResourceDefinition']:
     scoped.append({'kind':kind,'name':name,'release':label,'rules':o.get('rules',[]),'roleRef':o.get('roleRef'),'subjects':o.get('subjects',[])})
    if kind=='Service':
     services.append({'name':name,'namespace':namespace,'type':spec.get('type','ClusterIP')})
     if spec.get('type','ClusterIP')!='ClusterIP' or spec.get('externalIPs'):errors.append(f'Public service {name}')
    if kind in ['Prometheus','Alertmanager']:ps=spec;containers=[{'name':kind.lower(),'resources':spec.get('resources',{}),'image':spec.get('image','OPERATOR_DEFAULT_IMAGE_UNRESOLVED')}];mode='operator CR; reloader budget added separately'
    else:
     ps=spec.get('template',{}).get('spec',{}) if kind!='Pod' else spec
     if kind=='CronJob':ps=spec.get('jobTemplate',{}).get('spec',{}).get('template',{}).get('spec',{})
     if not ps:continue
     containers=ps.get('containers',[]);mode='rendered Pod template'
     for container in containers:
      args=container.get('args',[])
      if any(x.startswith('--kubelet-service=') for x in args):errors.append('Operator would maintain kube-system kubelet Service')
      if name.endswith('-operator') and '--namespaces=observability' not in args:errors.append('Operator watch namespace not restricted')
      for arg in args:
       if arg.startswith('--prometheus-config-reloader='):images.append({'release':label,'workload':'operator-generated-reloaders','container':'config-reloader','reference':arg.split('=',1)[1],'structuralFixture':False,'registryVerified':False,'digestPinned':bool(re.search(r'@sha256:[a-f0-9]{64}$',arg)),'status':'UNRESOLVED: generated sidecar registry identity not verified'})
    if not placed(ps):errors.append(f'Placement failed {kind}/{name}')
    if ps.get('hostNetwork') or ps.get('hostPID') or ps.get('hostIPC'):errors.append(f'Unexpected host namespace {name}')
    row={'kind':kind,'name':name,'namespace':namespace,'hook':o['metadata'].get('annotations',{}).get('helm.sh/hook'),'placement':placed(ps),'mode':mode,'containers':[]}
    for init,cset in [(False,containers),(True,ps.get('initContainers',[]))]:
     for c in cset:
      res=c.get('resources',{});missing=any(key not in res.get(side,{}) for side in ['requests','limits'] for key in ['cpu','memory'])
      if missing:errors.append(f'Unbounded resources {kind}/{name}/{c["name"]}')
      if not missing and not init:
       for i,(side,key) in enumerate([('requests','cpu'),('requests','memory'),('limits','cpu'),('limits','memory')]):totals[i]+=quantity(res[side][key],key=='memory')
      ref=c.get('image','');images.append({'release':label,'workload':name,'container':c['name'],'reference':ref,'structuralFixture':ref.startswith('example.invalid/') or ('a'*64 in ref),'registryVerified':False,'digestPinned':bool(re.search(r'@sha256:[a-f0-9]{64}$',ref)),'status':'UNRESOLVED: no registry verification'})
      row['containers'].append({'name':c['name'],'init':init,'resources':res})
    workloads.append(row)
 # Helm CRDs are not emitted by template unless requested; inventory separately from exact archive.
 with tarfile.open(chart) as t:
  for member in t.getmembers():
   if '/crds/crds/' in member.name and member.name.endswith(('.yaml','.yml')):
    for o in yaml.load_all(t.extractfile(member), Loader=yaml.BaseLoader):
     if o and o.get('kind')=='CustomResourceDefinition':scoped.append({'kind':o['kind'],'name':o['metadata']['name'],'release':'monitoring','source':member.name,'collisionStatus':'LIVE OWNERSHIP/SCHEMA UNVERIFIED'})
 # Two operator-managed reloaders, resources from reviewed operator setting.
 for n in ['prometheus','alertmanager']:
  workloads.append({'kind':'OperatorGeneratedSidecar','name':n+'-config-reloader','placement':'inherits parent CR','containers':[{'resources':{'requests':{'cpu':'10m','memory':'32Mi'},'limits':{'cpu':'100m','memory':'64Mi'}}}],'status':'verify actual operator-generated Pods before traffic'})
  totals=[x+y for x,y in zip(totals,[10,32,100,64])]
 assert placed({'nodeSelector':EXPECTED,'tolerations':[TOL]})
 assert not placed({'nodeSelector':{'kubernetes.io/hostname':'ip-172-31-25-57'},'tolerations':[TOL]})
 assert not placed({'nodeSelector':EXPECTED,'tolerations':[]})
 report={'scope':'OFFLINE ONLY; no AWS/Kubernetes changes','realImagePinsRequired':a.require_real_images,'structuralFixtureCount':sum(bool(x.get('structuralFixture')) for x in images),'chartSHA256':SHA,'structuralResult':'PASS' if not errors else 'FAIL','errors':errors,'admissionHooksTestOnly':a.test_admission_hooks,'deploymentDecision':'NO-GO','blockers':['Scoped Kubernetes pull credentials unprovisioned; inspect Phase2B/2C receipts for image publication status','Grafana credential not provisioned/verified','Live CRD/RBAC collision and storage-class checks pending','Actual operator-generated Pod specs/reloader defaults require live verification','Slack disabled; no webhook or delivery evidence'],'workloads':workloads,'resourceTotalsIncludingEnabledLoadAndReloaderAllowance':dict(zip(['cpuRequestMillicores','memoryRequestMi','cpuLimitMillicores','memoryLimitMi'],totals)),'services':services,'objects':objects,'negativePlacementTests':'wrong node and missing toleration rejected'}
 receipts=ROOT/'aws/phase2a/registry-verification.json'
 if receipts.exists():
  verified=[r for r in json.loads(receipts.read_text()) if r.get('registryVerified')]
  publication=ROOT/'aws/phase2b/verified-images.json'
  if publication.exists():verified.extend(r for r in json.loads(publication.read_text()) if r.get('registryVerified'))
  remaining=ROOT/'aws/phase2c/verified-images.json'
  if remaining.exists():verified.extend(r for r in json.loads(remaining.read_text()) if r.get('registryVerified'))
  for image in images:
   for r in verified:
    repo,digest=r['reference'].rsplit('@',1)
    if image['reference'].startswith(repo) and image['reference'].endswith('@'+digest):image.update({'registryVerified':True,'amd64Verified':r.get('amd64Verified',False),'status':'Registry manifest/config verified read-only; AWS pull untested','verificationReceipt':'phase2a/registry-verification.json'})
 (out/'render-audit.json').write_text(json.dumps(report,indent=2));(out/'image-inventory.json').write_text(json.dumps(images,indent=2));(out/'cluster-scoped.json').write_text(json.dumps(scoped,indent=2))
 print(json.dumps({k:report[k] for k in ['structuralResult','errors','deploymentDecision','resourceTotalsIncludingEnabledLoadAndReloaderAllowance']},indent=2))
 return bool(errors)
if __name__=='__main__':raise SystemExit(main())
