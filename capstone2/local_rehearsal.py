"""Local-kind-only evidence collection and controlled catalogue incident.

Never discovers a default kubeconfig or touches AWS. Does not retrieve Secrets.
Installation commands and image import are documented in LOCAL-RUN.md.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import socket
import time
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kubeconfig', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--incident', action='store_true')
    args = parser.parse_args()
    cfg = Path(args.kubeconfig).resolve()
    root = Path(__file__).resolve().parents[1]
    if cfg.is_relative_to(root):
        raise SystemExit('Keep private kubeconfig outside the repository')
    prefix = ['kubectl', '--kubeconfig', str(cfg)]

    def command(arguments):
        return subprocess.check_output(prefix + ['--request-timeout=15s'] + arguments, text=True, timeout=30)

    config = json.loads(command(['config', 'view', '-o', 'json']))
    servers = [c['cluster']['server'] for c in config['clusters']]
    if not servers or not all(s.startswith('https://127.0.0.1:') for s in servers):
        raise SystemExit('STOP: only loopback kind API servers permitted')
    nodes = json.loads(command(['get', 'nodes', '-o', 'json']))['items']
    if len(nodes) != 1 or nodes[0]['metadata']['name'] != 'capstone-rollback-lab-control-plane':
        raise SystemExit('STOP: wrong local cluster')
    out = Path(args.evidence).resolve()
    out.mkdir(parents=True, exist_ok=True)

    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

    def fetch(url):
        script = "fetch(process.argv[1],{signal:AbortSignal.timeout(7000)}).then(async r=>console.log(JSON.stringify({status:r.status,body:await r.text()}))).catch(e=>{console.error(e.message);process.exit(1)})"
        return json.loads(command(['exec', '-n', 'robot-shop', 'deploy/web', '--', 'node', '-e', script, url]))

    for namespace in ('robot-shop', 'observability'):
        pods = json.loads(command(['get', 'pods', '-n', namespace, '-o', 'json']))['items']
        save(namespace + '-pods.json', [{'name': p['metadata']['name'], 'phase': p['status']['phase'],
            'conditions': p['status'].get('conditions', []),
            'containers': [{'name': c['name'], 'ready': c['ready'], 'restarts': c['restartCount'],
                            'image': c['image'], 'imageID': c.get('imageID')}
                           for c in p['status'].get('containerStatuses', [])]} for p in pods])
    for service in ('web', 'catalogue', 'cart', 'payment'):
        save(service + '-metrics.json', fetch('http://' + service + ':8080/metrics'))
    save('catalogue-products.json', fetch('http://web:8080/api/catalogue/products'))
    # Query through a temporary loopback API tunnel, without broadening policies.
    # Jaeger 2.22 uses the stable v3 HTTP API; v1 internal endpoints return 404.
    candidates = json.loads(command(['get', 'pods', '-n', 'observability', '-l', 'app=jaeger', '-o', 'json']))['items']
    ready = [p for p in candidates if not p['metadata'].get('deletionTimestamp') and
             any(c['type'] == 'Ready' and c['status'] == 'True' for c in p['status'].get('conditions', []))]
    if len(ready) != 1:
        raise SystemExit('STOP: exactly one Ready Jaeger Pod required for trace evidence')
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    tunnel = subprocess.Popen(prefix + ['port-forward', '-n', 'observability',
        'pod/' + ready[0]['metadata']['name'], str(port) + ':16686', '--address', '127.0.0.1'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for attempt in range(30):
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=.2):
                    break
            except OSError:
                time.sleep(.2)
        else:
            raise RuntimeError('Jaeger loopback tunnel unavailable')
        now = datetime.datetime.now(datetime.timezone.utc)
        query = urllib.parse.urlencode({'query.service_name': 'catalogue',
            'query.start_time_min': (now - datetime.timedelta(minutes=20)).isoformat(),
            'query.start_time_max': now.isoformat(), 'query.search_depth': '5'})
        for name, path in [('jaeger-v3-services.json', '/api/v3/services'),
                           ('jaeger-v3-catalogue-traces.json', '/api/v3/traces?' + query)]:
            with urllib.request.urlopen('http://127.0.0.1:' + str(port) + path, timeout=20) as response:
                lines = response.read().decode().splitlines()
                save(name, [json.loads(line) for line in lines if line.strip()])
    finally:
        tunnel.terminate()
        try:
            tunnel.wait(timeout=10)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait(timeout=5)
    if not args.incident:
        return
    deployment = json.loads(command(['get', 'deployment', 'catalogue', '-n', 'robot-shop', '-o', 'json']))
    if deployment['spec']['replicas'] != 1 or deployment['status'].get('availableReplicas') != 1:
        raise SystemExit('STOP: healthy one-replica catalogue required')
    timeline = []

    def record(event):
        timeline.append({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'event': event})
        save('incident-timeline.json', timeline)

    record('Starting local-only catalogue availability drill; no database changes')
    try:
        command(['scale', 'deployment/catalogue', '-n', 'robot-shop', '--replicas=0'])
        record('Scaled catalogue to zero')
        for sample in range(4):
            time.sleep(30)
            save('incident-probe-' + str(sample) + '.json', fetch('http://web:8080/api/catalogue/products'))
        save('incident-alerts.json', fetch('http://monitoring-prometheus.observability:9090/api/v1/alerts'))
    finally:
        command(['scale', 'deployment/catalogue', '-n', 'robot-shop', '--replicas=1'])
        record('Restored catalogue replica count to one; readiness still must be verified')
    subprocess.run(prefix + ['rollout', 'status', 'deployment/catalogue', '-n', 'robot-shop', '--timeout=120s'], check=True, timeout=130)
    save('incident-recovery.json', fetch('http://web:8080/api/catalogue/products'))
    record('Catalogue rollout completed; inspect recovery HTTP result before declaring success')


if __name__ == '__main__':
    main()
