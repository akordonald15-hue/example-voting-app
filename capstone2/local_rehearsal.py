"""Local-kind-only evidence collection and controlled catalogue incident.

Never discovers a default kubeconfig or touches AWS. Does not retrieve Secrets.
Installation commands and image import are documented in LOCAL-RUN.md.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import time


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
    save('jaeger-services.json', fetch('http://jaeger.observability:16686/api/services'))
    save('jaeger-catalogue-traces.json', fetch('http://jaeger.observability:16686/api/traces?service=catalogue&limit=5'))
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
