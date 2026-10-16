"""Read-only, allowlisted Hermes metadata probe. Never reads chats or credentials."""
import json
import os
import sqlite3
from pathlib import Path


def inspect_db(path, tables):
    conn = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=2)
    conn.execute('PRAGMA query_only=ON')
    result = {}
    with conn:
        for table in tables:
            columns = [r[1] for r in conn.execute(f'PRAGMA table_info({table})')]
            result[table] = {'columns': columns}
            if columns:
                result[table]['rows'] = conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
        if 'tasks' in tables:
            result['task_status_counts'] = list(conn.execute('SELECT status,count(*) FROM tasks GROUP BY status'))
            result['block_kind_counts'] = list(conn.execute('SELECT block_kind,count(*) FROM tasks WHERE status IN (\'blocked\',\'todo\') GROUP BY block_kind'))
            result['run_outcome_counts'] = list(conn.execute('SELECT outcome,count(*) FROM task_runs GROUP BY outcome'))
        if 'sessions' in tables:
            result['cost_coverage'] = dict(zip(['sessions','with_actual','with_positive_estimate','with_calls'], conn.execute('SELECT count(*),count(actual_cost_usd),sum(estimated_cost_usd>0),sum(api_call_count>0) FROM sessions').fetchone()))
            result['cost_status_counts'] = list(conn.execute('SELECT cost_status,count(*) FROM sessions GROUP BY cost_status'))
            result['cost_source_counts'] = list(conn.execute('SELECT cost_source,count(*) FROM sessions GROUP BY cost_source'))
    conn.close()
    return result


if __name__ == '__main__':
    home = Path(os.environ.get('HERMES_HOME', '~/.hermes')).expanduser()
    board = Path(os.environ['HERMES_KANBAN_DB'])
    print(json.dumps({'kanban': inspect_db(board, ['tasks','task_links','task_runs','task_events']), 'sessions': inspect_db(home / 'state.db', ['sessions','session_model_usage'])}, indent=2))
