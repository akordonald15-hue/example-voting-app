"""Read-only policy check for a saved worker Terraform plan; never applies it."""
import argparse,json,subprocess
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('plan');args=parser.parse_args()
root=Path(__file__).resolve().parent
plan=json.loads(subprocess.check_output(['terraform','-chdir='+str(root),'show','-json',str(Path(args.plan).resolve())],text=True))
changes=[r for r in plan['resource_changes'] if r['mode']=='managed']
assert len(changes)==17, 'Unexpected resource count'
assert all(r['change']['actions']==['create'] for r in changes), 'Only additions permitted'
instances=[r for r in changes if r['type']=='aws_instance'];assert len(instances)==1 and instances[0]['name']=='worker'
a=instances[0]['change']['after'];assert a['instance_type']=='m7i.xlarge'
assert a['root_block_device'][0]['encrypted'] and a['root_block_device'][0]['volume_size']==50
assert a['metadata_options'][0]['http_tokens']=='required'
assert not a.get('key_name'), 'No SSH key permitted'
for r in changes:
 if r['type']=='aws_vpc_security_group_ingress_rule':
  v=r['change']['after'];assert not v.get('cidr_ipv4') and not v.get('cidr_ipv6'), 'No CIDR ingress permitted'
  assert (v['ip_protocol'],v['from_port'],v['to_port']) in [('tcp',6443,6443),('tcp',10250,10250),('udp',8472,8472)]
text=(root/'cloud-init.yaml.tftpl').read_text()
assert 'ConditionPathExists=/etc/rancher/k3s/agent-token' in text
assert '--token-file /etc/rancher/k3s/agent-token' in text
assert 'systemctl enable' not in text and 'systemctl start k3s' not in text
print('PASS:17 additions; isolated worker; private ingress only; encrypted disk/IMDSv2; no automatic join')
