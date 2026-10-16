---
name: tortuga-research
description: Scope changes and define verifiable quality gates.
version: 0.1.0
author: Tortuga-AI contributors, Hermes Agent
license: LicenseRef-Upstream-Unverified
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, tortuga, local-first]
    related_skills: [tortuga-implement]
---
# Tortuga Research
Portable research phase; no dispatcher or automatic task creation.

## When to Use
Investigate a change before implementing; extend valid prior research rather than
repeat it. Do not use research as permission to implement unresolved product choices.

## Prerequisites
Read project AGENTS.md, task requirements and prior evidence with `read_file`.
Use `terminal` for Git status/branch/HEAD before editing; preserve other writers' files.
Do not switch a shared checkout. An unborn HEAD is not a reproducible Git baseline:
record it as null and use file hashes for a bounded local trial, not a benchmark.
Use only explicitly authorized paths and actions. No credentials, live services,
profile installation, commit, push or PR without separate permission.

## Procedure
1. Read code, docs and relevant project skills using `search_files` and `read_file`.
   Distinguish confirmed requirements, proposals, policy exceptions and unknowns.
2. Ask whether the change is needed; search existing code, stdlib, native features
   and existing dependencies before new abstractions. Compare root-cause fixes with
   symptom patches; state effort and tradeoffs. Prefer a proportionate root-cause fix.
3. Resolve implementation details from evidence. Escalate unresolved user-visible
   defaults, conflicting policies or permissions with a recommendation and reason.
4. Define quality BEFORE next steps: observability, testability, maintainability,
   simplicity; SOLID/OOP and pagination when applicable (otherwise explain N/A).
5. Define acceptance IDs and unit/integration/negative/boundary tests, a known-defect
   control, exact full-suite command, timeout and expected count. Missing tooling is
   blocked, not pass. Check manual instructions against actual CLI/docs.
6. Write `research.md` in the agreed run directory with BLUF, sources, options,
   open questions, quality plan, test strategy, allowed files and implement handoff.
   End with `SCOPE: SINGLE_TASK` or `SCOPE: NEEDS_DECOMPOSITION`. Decomposition is a
   proposal only: do not create tickets, dispatch agents or move Kanban state.

## Pitfalls
Runner branch creation is not implicit in Hermes. Do not assume a branch/worktree
already exists or create one in a shared checkout without coordination.
Never compress security warnings, permission gates or uncertainty out of reports.
Do not copy secrets into reports or pass credentials to processes by implication.
writing-plans, planning-tests and implementing-tasks are not prerequisites.

## Verification
Every acceptance ID has a planned check and owner; product questions are resolved
or explicitly block implementation. Record skill version/hash and source revision.
