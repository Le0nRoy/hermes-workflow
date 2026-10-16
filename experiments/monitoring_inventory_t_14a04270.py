"""Read-only monitoring inventory; never prints container env or secrets."""
import json
import os
import pathlib
import subprocess
import urllib.request
import yaml

ROOT = pathlib.Path(os.environ['TORTUGA_AI_ROOT']) / 'monitoring'

def get(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.load(response)

ips = {}
for name in ['prometheus', 'grafana', 'alertmanager', 'node_exporter']:
    data = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    nets = data['NetworkSettings']['Networks']
    ips[name] = next(iter(nets.values()))['IPAddress']
    print('RUNTIME', name, {'state': data['State']['Status'], 'mounts': [(m['Source'], m['Destination'], m['RW']) for m in data['Mounts']], 'networks': list(nets)})
    if name == 'node_exporter':
        print('node args', data['Config']['Cmd'])
    if name == 'grafana':
        print('grafana access', [v for v in data['Config']['Env'] if v.startswith(('GF_AUTH_ANONYMOUS', 'GF_USERS_ALLOW_SIGN_UP'))])
for path in sorted((ROOT / 'grafana/provisioning/dashboards').glob('*.json')):
    data = json.loads(path.read_text())
    print('DASHBOARD', path.name, data.get('uid'), data.get('title'), 'panels', len(data.get('panels', [])))
    print('TITLES', [p.get('title') for p in data.get('panels', [])])
for filename in ['grafana/provisioning/datasources/prometheus.yml', 'grafana/provisioning/dashboards/dashboards.yml', 'grafana/provisioning/alerting/notification-policy.yml']:
    print(filename, (ROOT / filename).read_text())
data = yaml.safe_load((ROOT / 'grafana/provisioning/alerting/rules.yml').read_text())
for group in data.get('groups', []):
    print('GRAFANA_RULES', group.get('name'), [{k: rule.get(k) for k in ['title', 'for', 'labels', 'noDataState', 'execErrState']} for rule in group['rules']])
for filename in ['alertmanager/alertmanager.yml', 'grafana/provisioning/alerting/contacts.yml']:
    data = yaml.safe_load((ROOT / filename).read_text())
    print('ROUTING', filename)
    if 'route' in data:
        print(data['route'])
        print('receivers', [(r['name'], list(r)) for r in data['receivers']])
        print('inhibit', data.get('inhibit_rules'))
    else:
        print([(p['name'], [(r['type'], sorted(r.get('settings', {}))) for r in p['receivers']]) for p in data.get('contactPoints', [])])
base = 'http://' + ips['prometheus'] + ':9090'
for endpoint in ['/api/v1/targets', '/api/v1/rules']:
    try:
        data = get(base + endpoint)['data']
        if 'activeTargets' in data:
            print('LIVE_TARGETS', [{'job': t['labels'].get('job'), 'health': t['health'], 'lastScrape': t['lastScrape'], 'error_present': bool(t['lastError'])} for t in data['activeTargets']])
        else:
            print('LIVE_RULES', [{'name': r['name'], 'health': r.get('health'), 'state': r.get('state')} for g in data['groups'] for r in g['rules']])
    except Exception as exc:
        print('FAILED', endpoint, type(exc).__name__)
for endpoint in ['/api/health', '/api/search?type=dash-db', '/api/datasources']:
    try:
        data = get('http://127.0.0.1:3000' + endpoint)
        if endpoint.startswith('/api/search'):
            data = [{k: d.get(k) for k in ['uid', 'title']} for d in data]
        elif endpoint == '/api/datasources':
            data = [{k: d.get(k) for k in ['uid', 'type', 'name', 'url']} for d in data]
        print('LIVE_GRAFANA', endpoint, data)
    except Exception as exc:
        print('FAILED', endpoint, type(exc).__name__)
