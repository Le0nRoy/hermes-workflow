# Project-local Tortuga adaptations

These are portable source artifacts, version 0.1.0, not installed profile skills.
Use `read_file` on the chosen `skills/tortuga-*/SKILL.md` and its referenced files in
an authorized Hermes session. Do not assume slash commands or discovery are enabled.

- `tortuga-research`: scope, policy/quality decisions and test strategy.
- `tortuga-implement`: red/green changes, full-suite ownership and evidence.
- `tortuga-review`: local code/evidence review, staff/security checks and human gate.

No mandatory writing-plans, planning-tests or implementing-tasks. No auto-dispatch,
profile changes, original Tortuga edits or publications. Install/configure only in a
separately authorized task after verifying the installed Hermes CLI/docs and selected
profile. Keep source and installed hashes, rollback plan and human acceptance separate.

Source attribution: Tortuga-AI contributors; adaptations prepared with Hermes Agent.
No LICENSE/COPYING file was found among tracked upstream files at the recorded revision.
`LicenseRef-Upstream-Unverified` is a warning, NOT a grant of redistribution rights.
Resolve licensing before public redistribution. Local permission comes from this task.

Provenance, differences and actual trial: [report](../docs/tortuga-workflow-adaptation.md).
Verification from repo root via `terminal`:
`python -B -m unittest discover -s tests/skills -p 'test_tortuga_skills.py' -v`.
