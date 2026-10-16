#!/usr/bin/env python3
"""Credential-free Linux sandbox. This is a lab launcher, not a Hermes emulator."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

LANES = ('worker', 'dispatcher', 'quota')
HERE = Path(__file__).resolve().parent


def run(lane, script, seconds):
    # Never reuse an existing directory or inherit HOME, tokens, socket paths,
    # HERMES_KANBAN_TASK, board pins, Python startup hooks or proxy settings.
    scratch = Path(os.environ.get('TMPDIR', str(Path.home() / '.hermes/cache/scratch')))
    scratch.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f'recovery-{lane}-', dir=scratch))
    root.chmod(0o700)
    argv = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent',
            '--new-session', '--cap-drop', 'ALL', '--ro-bind', '/usr', '/usr',
            '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib', '/lib64',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
            '--dir', '/home', '--dir', '/run', '--bind', str(root), '/lab',
            '--ro-bind', str(script), '/case.py', '--chdir', '/lab',
            '--clearenv', '--setenv', 'PATH', '/usr/bin',
            '--setenv', 'HOME', '/lab/home', '--setenv', 'TMPDIR', '/tmp',
            '--setenv', 'HERMES_HOME', '/lab/home',
            '--setenv', 'HERMES_KANBAN_DB', '/lab/queue.db',
            '--setenv', 'HERMES_KANBAN_BOARD', f'recovery-{lane}',
            '--setenv', 'HERMES_KANBAN_WORKSPACES_ROOT', '/lab/workspaces',
            '--setenv', 'HERMES_KANBAN_ATTACHMENTS_ROOT', '/lab/attachments',
            '--setenv', 'LAB_LANE', lane,
            '/usr/bin/python3', '-I', '-B', '/case.py']
    started = time.monotonic()
    # GNU timeout owns only this newly spawned sandbox; no host PID lookup/kill.
    result = subprocess.run(['/usr/bin/timeout', '--signal=TERM', '--kill-after=5',
                             str(seconds), *argv],
                            env={'PATH': '/usr/bin'}, capture_output=True, text=True,
                            timeout=seconds + 15)
    record = {'lane': lane, 'root': str(root), 'returncode': result.returncode,
              'elapsed_seconds': round(time.monotonic() - started, 3),
              'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
              'stdout': result.stdout, 'stderr': result.stderr,
              'mode': 'isolation-preflight-not-Hermes-recovery'}
    (root / 'launcher-result.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=(*LANES, 'all'), default='all')
    parser.add_argument('--script', type=Path, default=HERE / 'probe.py')
    parser.add_argument('--seconds', type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 180:
        parser.error('--seconds must be 1..180')
    script = args.script.resolve(strict=True)
    if not script.is_relative_to(HERE) or not script.is_file():
        parser.error('script must be a file inside experiments/recovery-lab')
    lanes = LANES if args.lane == 'all' else (args.lane,)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(lambda lane: run(lane, script, args.seconds), lanes))
    print(json.dumps(results, indent=2))
    return int(any(item['returncode'] != 0 for item in results))


if __name__ == '__main__':
    raise SystemExit(main())
