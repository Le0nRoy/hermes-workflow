---
name: tortuga-implement
description: Implement bounded changes with real test evidence.
version: 0.1.0
author: Tortuga-AI contributors, Hermes Agent
license: LicenseRef-Upstream-Unverified
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, tortuga, local-first]
    related_skills: [tortuga-research, tortuga-review]
---
# Tortuga Implement
Portable local implementation; explicitly replaces missing runner duties.

## When to Use
Implement an authorized researched change. Pure investigation belongs in research.

## Prerequisites
Read project AGENTS.md, task requirements and prior evidence with `read_file`.
Use `terminal` for Git status/branch/HEAD before editing; preserve other writers' files.
Do not switch a shared checkout. An unborn HEAD is not a reproducible Git baseline:
record it as null and use file hashes for a bounded local trial, not a benchmark.
Use only explicitly authorized paths and actions. No credentials, live services,
profile installation, commit, push or PR without separate permission.

## Procedure
1. Read `research.md`; resolve gates before editing. Claim a non-overlapping list of
   files organizationally; a shared UID/worktree is not a security sandbox.
2. Write a behavior test, run it through `terminal`, inspect the expected failure,
   then implement the minimum fix with `write_file`/`patch`. Repeat red/green/refactor.
   Never weaken assertions, add skips or delete tests to hide failures.
3. Run affected tests and lint. Include success and rejection cases, isolated data,
   cleanup in finally/context managers, bounded waits rather than blind sleeps.
   Preserve observability and pagination decisions; trace new config from declaration
   through each consumer. Do not install packages/services implicitly.
4. For UI changes read `references/frontend-validation.md`. Static lint does not
   establish browser behavior. Missing browser evidence remains not tested.
5. Run the FULL agreed suite via `terminal` with an explicit timeout in seconds;
   capture command, cwd, timestamps, exit code, test IDs/count, skips and hashes.
   Do not pipe away the real exit code. A timeout, zero tests or unexpected skip fails.
6. Write `implement.md`: changed files, deviations, red/green and full-suite evidence,
   limitations, dependency changes and reviewer instructions. Update affected docs.

## Runner responsibilities
| Duty formerly supplied by Tortuga runner | Owner here |
|---|---|
| Full suite | Implementer invokes deterministic project command; not automatic Hermes behavior |
| Evidence and attribution | Implementer records actual outputs, model/provider and unknown costs |
| Review rerun | Reviewer may repeat bounded agreed checks; human owns final acceptance |
| Commit/push/PR | Human gate; disabled in local-only trial; no hidden publisher |
| Retry/recovery | Operator after diagnosis, at most one explicitly authorized retry in pilot |
| Dispatcher claim/reclaim | Existing separately configured dispatcher, NOT this skill |

## Pitfalls
Stop on quota/429, timeout, approval denial or unsafe changes; save a handoff, do not
switch provider or retry indefinitely. A fix iteration is not permission to restart
a failed worker. Record every attempt separately. Do not infer isolation from Docker
availability. Pre-existing failure requires baseline reproduction, not a guess.
Do not commit merely to save progress: leave authorized files and a handoff instead.
writing-plans, planning-tests and implementing-tasks are not prerequisites.

## Verification
All acceptance IDs mapped to results; full suite genuinely executed on current files;
known defect rejected; no unapproved changes/publication. Unknowns stay unknown.
