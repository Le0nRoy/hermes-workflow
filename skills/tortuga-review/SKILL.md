---
name: tortuga-review
description: Review code, security and current verification evidence.
version: 0.1.0
author: Tortuga-AI contributors, Hermes Agent
license: LicenseRef-Upstream-Unverified
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workflow, tortuga, local-first]
    related_skills: [tortuga-research, tortuga-implement]
---
# Tortuga Review
Review local files without requiring a PR. This does not grant publication rights.

## When to Use
Assess implemented changes and evidence. Same-session review is self-review, never
claim independent review; final human acceptance is a separate gate.

## Prerequisites
Read project AGENTS.md, task requirements and prior evidence with `read_file`.
Use `terminal` for Git status/branch/HEAD before editing; preserve other writers' files.
Do not switch a shared checkout. An unborn HEAD is not a reproducible Git baseline:
record it as null and use file hashes for a bounded local trial, not a benchmark.
Use only explicitly authorized paths and actions. No credentials, live services,
profile installation, commit, push or PR without separate permission.

## Procedure
1. Read research, implementation, actual changed files (including untracked files),
   hashes and full-suite evidence. Stale hashes require fresh checks, not approval.
2. Apply `references/review-checks.md`: staff-engineer alignment FIRST, then security.
   Match every acceptance ID; include extras, missing scope and unexplained deviations.
3. Check correctness, boundaries, config propagation, failure outputs, observability,
   maintainability, simplicity and test strength. Avoid invented architecture mandates.
4. Unlike upstream, repeat bounded agreed tests via `terminal` when helpful: there is
   no guaranteed external runner. Check exact IDs/count and zero unexpected skips.
   Missing, skipped, timed-out or not-started CI/E2E is not a pass. Local unit evidence
   does not establish E2E. Confirm the known-defect control fails for the intended bug.
5. Write `review.md` beginning `VERDICT: APPROVE` or `VERDICT: REQUEST_CHANGES`.
   Any unresolved finding or missing required evidence means REQUEST_CHANGES.
   State review scope and confidence. Include Staff Engineer
   Analysis, Security Analysis, verification, findings (severity/path/line/fix),
   limitations and human gate. No automatic merge, publish, ticket or board action.

## Pitfalls
Do not trust a green summary without commands/output/current hashes. Never call a
same-agent role change independent review. No /tmp report convention or runner footer
is assumed; write only in the agreed run directory. Security review is static analysis,
not a sandbox audit, penetration test or client-data clearance.

## Verification
Report accounts for every criterion and changed file, reproduces significant checks,
and clearly distinguishes local approval from independent human acceptance.
