-- Synthetic, no real task or session data. Run: sqlite3 :memory: '.read experiments/hermes-metrics-fixture.sql'
CREATE TABLE tasks (id TEXT PRIMARY KEY, status TEXT, block_kind TEXT);
CREATE TABLE task_links (parent_id TEXT, child_id TEXT);
CREATE TABLE task_runs (id INTEGER PRIMARY KEY, task_id TEXT, outcome TEXT, started_at INTEGER, ended_at INTEGER);
INSERT INTO tasks VALUES ('p','running',NULL), ('wait','todo',NULL), ('gate','blocked','needs_input'), ('failed','ready',NULL), ('ok','done',NULL);
INSERT INTO task_links VALUES ('p','wait');
INSERT INTO task_runs VALUES (1,'ok','completed',100,110),(2,'failed','crashed',100,105),(3,'p',NULL,100,NULL);
SELECT 'statuses',status,count(*) FROM tasks GROUP BY status ORDER BY status;
SELECT 'dependency_wait',count(*) FROM tasks t WHERE t.status='todo' AND EXISTS (SELECT 1 FROM task_links l JOIN tasks p ON p.id=l.parent_id WHERE l.child_id=t.id AND p.status!='done');
SELECT 'owner_gate',count(*) FROM tasks WHERE status='blocked' AND block_kind='needs_input';
SELECT 'finished_runs',count(*) FROM task_runs WHERE ended_at IS NOT NULL;
SELECT 'failure_runs',count(*) FROM task_runs WHERE outcome IN ('crashed','timed_out','spawn_failed','gave_up');
SELECT 'active_not_failure',count(*) FROM task_runs WHERE outcome IS NULL AND ended_at IS NULL;
-- NULL means no billing evidence; it must never become a zero-valued observed charge.
CREATE TABLE costs (session TEXT, cost_status TEXT, estimated REAL, actual REAL);
INSERT INTO costs VALUES ('unknown','unknown',NULL,NULL),('included','included',0.0,NULL),('estimate','estimated',2.5,NULL);
SELECT 'observed_actual',count(*) FROM costs WHERE cost_status='actual' AND actual IS NOT NULL;
SELECT 'unknown_cost',count(*) FROM costs WHERE actual IS NULL AND estimated IS NULL;
