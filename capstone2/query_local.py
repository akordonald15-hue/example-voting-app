"""Read-only local-kind telemetry query through a short-lived loopback tunnel."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--kubeconfig', required=True)
parser.add_argument('--service', choices=['loki', 'monitoring-prometheus', 'jaeger', 'monitoring-grafana'], required=True)
parser.add_argument('--path', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
prefix = ['kubectl', '--kubeconfig', args.kubeconfig]
config = json.loads(subprocess.check_output(prefix + ['config', 'view', '-o', 'json']))
assert all(c['cluster']['server'].startswith('https://127.0.0.1:') for c in config['clusters']), 'local cluster only'
nodes = json.loads(subprocess.check_output(prefix + ['get', 'nodes', '-o', 'json', '--request-timeout=15s']))
assert [n['metadata']['name'] for n in nodes['items']] == ['capstone-rollback-lab-control-plane'], 'wrong node'
assert args.path.startswith('/') and not args.path.startswith('//'), 'relative API path required'
remote = {'loki': 3100, 'monitoring-prometheus': 9090, 'jaeger': 16686, 'monitoring-grafana': 80}[args.service]
with socket.socket() as reservation:
    reservation.bind(('127.0.0.1', 0))
    port = reservation.getsockname()[1]
tunnel = subprocess.Popen(prefix + ['port-forward', '-n', 'observability', 'service/' + args.service,
    str(port) + ':' + str(remote), '--address', '127.0.0.1'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for attempt in range(50):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=.2):
                break
        except OSError:
            time.sleep(.2)
    else:
        raise RuntimeError('loopback tunnel unavailable')
    with urllib.request.urlopen('http://127.0.0.1:' + str(port) + args.path, timeout=30) as response:
        data = response.read().decode()
        # Only save a valid JSON response; HTTP/API errors remain failures.
        parsed = json.loads(data)
        if isinstance(parsed, dict) and parsed.get('status') == 'error':
            raise RuntimeError('telemetry API returned an error')
        Path(args.output).write_text(json.dumps(parsed, indent=2) + '\n', encoding='utf-8')
        print('SAVED', args.output)
finally:
    tunnel.terminate()
    try:
        tunnel.wait(timeout=10)
    except subprocess.TimeoutExpired:
        tunnel.kill()
        tunnel.wait(timeout=5)
