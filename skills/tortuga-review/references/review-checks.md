# Review checks adapted from Tortuga sub-skills

## Staff Engineer Analysis
Compare planned acceptance items with actual files FIRST. Mark Done, Partial,
Missing or Extra. Calculate alignment with a tool (done/planned); a missing mandatory
item blocks approval regardless of score. Below upstream's 70% is critical.
Assess separation of concerns, correctness, error paths, coupling, complexity,
performance and positive/negative/boundary test coverage. Cite file:line and a
concrete remedy. No mandatory interfaces for single-use functions; document N/A.

## Security Analysis
Check injection (SQL, commands, templates, paths), authentication/authorization,
session lifecycle, secrets in code/output, crypto/TLS, input validation, XSS/SSRF,
dependency provenance and permissive/debug defaults. Trace externally controlled
values to sinks. State severity and exploit prerequisites; HIGH/CRITICAL block.
Use synthetic inputs only. Never open auth stores or scan unrelated home directories.
If no findings: say no issues found within inspected scope, not 'secure'. Record
untested categories. CVE freshness is unknown unless actually checked.

These checks are integrated references, not new profiles or nested agent spawns.
