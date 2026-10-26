"""Explicit local-only catalogue drill; always restores the captured replica count."""
import datetime,json,subprocess,time,urllib.parse
from pathlib import Path
from collect_kind import K, read, query, NODE
out=Path(__file__).resolve().parent/'evidence/runtime'
def save(name,value): (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def prom(expr): return json.loads(query('monitoring-prometheus',9090,'/api/v1/query?'+urllib.parse.urlencode({'query':expr})))
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--execute-local-drill',action='store_true',required=True);parser.parse_args()
    assert [n['metadata']['name'] for n in json.loads(read(['get','nodes','-o','json']))['items']]==[NODE]
    dep=json.loads(read(['get','deploy','catalogue','-n','robot-shop','-o','json']))
    assert dep['spec']['replicas']==1 and dep['status'].get('availableReplicas')==1
    baseline=prom('probe_success{job="robot-shop-availability"}');assert baseline['data']['result'][0]['value'][1]=='1', 'Healthy baseline required'
    save('incident-baseline.json',baseline);timeline=[]
    def mark(event):
        timeline.append({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event});save('incident-timeline.json',timeline)
    try:
        mark('Local catalogue-only drill starts; no database or AWS changes')
        read(['scale','deploy/catalogue','-n','robot-shop','--replicas=0']);mark('Catalogue scaled to zero')
        for i in range(5):
            time.sleep(30);save('incident-sample-'+str(i)+'.json',{'probe':prom('probe_success{job="robot-shop-availability"}'),'alerts':json.loads(query('monitoring-prometheus',9090,'/api/v1/alerts'))})
    finally:
        read(['scale','deploy/catalogue','-n','robot-shop','--replicas=1']);mark('Catalogue restored to one replica')
    subprocess.run(K+['rollout','status','deploy/catalogue','-n','robot-shop','--timeout=120s'],check=True,timeout=140)
    time.sleep(30);save('incident-recovery.json',{'probe':prom('probe_success{job="robot-shop-availability"}'),'alerts':json.loads(query('monitoring-prometheus',9090,'/api/v1/alerts'))});mark('Readiness restored; inspect probe and alert evidence')
