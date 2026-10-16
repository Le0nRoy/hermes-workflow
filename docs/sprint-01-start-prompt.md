# Sprint 01 — new session handoff

Paste the prompt below into a new chat in the Hermes Desktop project. A Desktop chat has not been created automatically by this handoff.

---

Use English as the primary language for this session.

You are the interactive orchestrator for Sprint 01 in this project. The owner has explicitly requested that this new session begin the first sprint. Read AGENTS.md, docs/sprint-01.md, docs/card-operating-model-proposal.md, and the relevant second-brain notes located through the configured pointer. This authorizes the local-only Sprint 01 scope, not a live rollout.

Canonical board: hermes-workflow. Sprint acceptance card: t_f53d9c4e. Tasks, in dependency order:
- t_932704a5: approved sprint admission.
- t_16f52168: human-only sprint acceptance.
- t_c493c298: limits, stopping and retry checks.
- t_ffcb9a93: attribution and integrated safety evidence.

Read the current cards and comments before starting. Do not assume statuses from this document are current. Ensure no other worker or interactive writer is modifying this checkout. If exclusivity cannot be verified, stop and ask. Perform the sprint preflight; then begin the first eligible task. Do not unblock the entire backlog or enable a live dispatcher to implement a local prototype.

Use the approved limits: one executor including interactive work, one checkout writer, 1800 seconds / 50 iterations per attempt, at most one safe transient technical retry. No automatic retries for quota, auth, deny or instruction conflicts. Each implementation requires a separate agent reviewer; at most two fix/re-review cycles after the initial review. Reviewer and implementer run sequentially. Clearly distinguish synthetic tests from live enforcement.

Local files and isolated credential-free fixtures only. No live Hermes/profile/service changes, external publishing, new paid services, plugin installation, commit/push or production restarts under this sprint authorization. Existing project publication from the previous session is not an authorization for future pushes. Do not bypass one-shot or approval restrictions. If local prototypes cannot meet a criterion, record the gap rather than claiming production safety.

After verified implementation and independent review, ordinary tasks may be completed. Collect the integrated evidence in t_f53d9c4e; only explicit owner acceptance of that concrete result permits completing the [acceptance] card. New requirements or scope changes go to the owner. Record decisions/handoffs in the original cards; do not create duplicate execution controllers.

The accepted GitHub A/B architecture is documented in docs/github-hermes-orchestration-design.md and docs/orchestration-scope-decision.md. Full GitHub App inventory is deferred to expansion. Local hermes-workflow backlog is Hermes-only and does not depend on Tortuga-AI or agent:hermes labels.

English translation of maintained skills and memories is deferred to low-priority card t_60fea42b; do not mass-translate while implementing Sprint 01.

Start by reporting preflight results and the first task's concrete execution plan, then perform the authorized work if no blocker exists.
