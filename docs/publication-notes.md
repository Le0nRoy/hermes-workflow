# Public snapshot and portability

This repository is a sanitized development snapshot, not a portable installer or a deployed orchestration service.

Machine-specific home/workspace paths and host names have been replaced with symbolic placeholders. Private network addresses in historical reports use documentation-range examples; these are not current probe targets. Resolve placeholders locally before using example commands. `${HERMES_HOME}` is the active profile home, not necessarily the default home. `${HERMES_WORKFLOW_ROOT}`, `${SECOND_BRAIN_ROOT}`, `${TORTUGA_AI_ROOT}`, and other project-root placeholders must be configured for the installation; JSON strings do not expand shell variables automatically.

Historical experiment evidence with sanitized paths is a redacted copy, not byte-identical original output. Existing provenance hashes refer to the original local artifacts and must not be used to authenticate redacted copies. Fresh experiments should generate new evidence and manifests; no historic experiment is claimed to have been rerun merely by publication.

Raw monitoring inventory and raw per-run experiment evidence are excluded from publication. Source fixtures, verification code, contracts and research summaries are included. Host paths and identifiers were pattern-scanned; this is not a guarantee that every possible identifying detail can be detected automatically.

The working knowledge base, credentials, live Kanban databases, sessions, local private backups and runtime configuration are not part of this repository. Local backups of pre-publication files were kept outside the checkout; they are not an independent disaster-recovery backup.

Research architecture was accepted within a limited pilot; full GitHub App inventory is deferred. Sprint 01 execution is requested for a new English-language operator chat after preflight. See sprint-01-start-prompt.md. No live service rollout is authorized by this snapshot.
