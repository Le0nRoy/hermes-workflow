"""Synthetic contract tests; no Hermes imports, network or live DB writes."""
import sqlite3
import unittest


def classify(status, *, owner_hold=False, open_parents=0, outcome=None,
             heartbeat_age=None, stale_after=300):
    """Proposed monitoring projection, NOT a replacement for Hermes routing."""
    if owner_hold and status in {'blocked', 'triage'}:
        return 'owner_hold'
    if status == 'todo' and open_parents:
        return 'dependency_wait'
    if status == 'running':
        if heartbeat_age is None:
            return 'telemetry_unknown'
        return 'stale_candidate' if heartbeat_age > stale_after else 'running'
    if status == 'ready' and outcome == 'rate_limited':
        return 'quota_retry'
    if status in {'blocked', 'triage'}:
        return 'needs_attention'
    return status


def cost_view(amount, status, source):
    """Numeric DB defaults alone never establish a monetary measurement."""
    if status == 'included':
        return ('subscription_included', None)
    if amount is None or status not in {'actual', 'estimated'}:
        return ('unknown', None)
    if not source or source == 'none':
        return ('unknown', None)
    return ('provider_reported' if status == 'actual' else 'estimated', amount)


class SemanticsTests(unittest.TestCase):
    def test_owner_hold_is_not_failure(self):
        self.assertEqual(classify('blocked', owner_hold=True, outcome='crashed'), 'owner_hold')

    def test_dependency_wait(self):
        self.assertEqual(classify('todo', open_parents=1), 'dependency_wait')
        self.assertEqual(classify('todo'), 'todo')

    def test_normal_run_supersedes_historical_error(self):
        self.assertEqual(classify('running', outcome='crashed', heartbeat_age=10), 'running')

    def test_stale_is_not_proven_crash(self):
        self.assertEqual(classify('running', heartbeat_age=301), 'stale_candidate')
        self.assertEqual(classify('running'), 'telemetry_unknown')

    def test_quota_not_code_failure(self):
        self.assertEqual(classify('ready', outcome='rate_limited'), 'quota_retry')
        self.assertEqual(classify('blocked', outcome='crashed'), 'needs_attention')

    def test_unknown_not_free(self):
        for amount in (None, 0, 1):
            self.assertEqual(cost_view(amount, 'unknown', 'none'), ('unknown', None))

    def test_subscription_not_invoice(self):
        self.assertEqual(cost_view(0, 'included', 'none'), ('subscription_included', None))

    def test_estimate_and_report_are_separate(self):
        self.assertEqual(cost_view(0.25, 'estimated', 'official_docs_snapshot'), ('estimated', 0.25))
        self.assertEqual(cost_view(0.25, 'actual', 'provider'), ('provider_reported', 0.25))
        self.assertEqual(cost_view(0, 'actual', 'none'), ('unknown', None))

    def test_dependency_query_and_terminal_runs(self):
        db = sqlite3.connect(':memory:')
        db.executescript('''
            CREATE TABLE tasks(id TEXT, status TEXT);
            CREATE TABLE task_links(parent_id TEXT, child_id TEXT);
            CREATE TABLE task_runs(id INTEGER, outcome TEXT, ended_at INTEGER);
            INSERT INTO tasks VALUES ('parent','running'),('child','todo'),('held','blocked');
            INSERT INTO task_links VALUES ('parent','child');
            INSERT INTO task_runs VALUES (1,'rate_limited',100),(2,NULL,NULL),(3,'completed',120);
        ''')
        count = db.execute('''SELECT count(*) FROM tasks t WHERE t.status='todo'
            AND EXISTS (SELECT 1 FROM task_links l JOIN tasks p ON p.id=l.parent_id
                WHERE l.child_id=t.id AND p.status NOT IN ('done','archived'))''').fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(db.execute('SELECT count(*) FROM task_runs WHERE ended_at IS NOT NULL').fetchone()[0], 2)
        db.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
