"""Read-only, unauthenticated monitoring inventory; never sends alerts."""
import json
import os
from typing import Any
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

PROM = os.environ['PROMETHEUS_URL'].rstrip('/')
GRAF = os.environ['GRAFANA_URL'].rstrip('/')

def get(base, path):
    try:
        with urllib.request.urlopen(base + path, timeout=10) as response:
            return json.load(response)
    except (OSError, ValueError) as exc:
        return {'error': type(exc).__name__, 'status': getattr(exc, 'code', None)}

out: dict[str, Any] = {'checked_at': datetime.now(timezone.utc).isoformat()}
data = get(PROM, '/api/v1/targets')
out['targets'] = [{k: t.get(k) for k in ('labels', 'health', 'lastScrape', 'lastError')} for t in data.get('data', {}).get('activeTargets', [])]
data = get(PROM, '/api/v1/rules')
out['rules'] = [{k: r.get(k) for k in ('name', 'query', 'duration', 'health', 'state', 'labels')} for g in data.get('data', {}).get('groups', []) for r in g.get('rules', [])]
out['datasources'] = get(GRAF, '/api/datasources')
if isinstance(out['datasources'], list):
    out['datasources'] = [{k: d.get(k) for k in ('uid', 'name', 'type', 'access', 'url')} for d in out['datasources']]
out['dashboards'] = []
search = get(GRAF, '/api/search?type=dash-db')
if isinstance(search, list):
    for row in search:
        d = get(GRAF, '/api/dashboards/uid/' + row['uid']).get('dashboard', {})
        panels = []
        def walk(items):
            for p in items:
                panels.append({'title': p.get('title'), 'queries': [t.get('expr') for t in p.get('targets', []) if t.get('expr')]})
                walk(p.get('panels', []))
        walk(d.get('panels', []))
        out['dashboards'].append({'uid': row['uid'], 'title': row['title'], 'panels': panels})
out['grafana_alert_rules_access'] = get(GRAF, '/api/v1/provisioning/alert-rules')
from urllib.parse import urlencode
out['queries'] = {}
for query in ['count by(job)(up)', 'count by(job)(__name__{__name__=~"litellm_.*"})', 'count(litellm_spend_metric)', 'count({__name__=~"hermes_.*"})', 'count(node_cpu_seconds_total)', 'count(container_cpu_usage_seconds_total)', 'count(agent_queue_depth)', 'count(ALERTS{alertstate="firing"})']:
    out['queries'][query] = get(PROM, '/api/v1/query?' + urlencode({'query': query}))
Path(__file__).with_name('inventory.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(out, ensure_ascii=False, indent=2))
