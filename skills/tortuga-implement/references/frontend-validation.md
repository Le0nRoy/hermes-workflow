# Frontend validation
Adapted from frontend-implement and webapp-testing. Detect existing framework and
pinned tools, do not force React versions or migrate JS to TS for unrelated work.
Use `terminal` to run existing typecheck/lint commands; inspect package scripts first.
Do not use package-download shortcuts or install browser system dependencies without
permission. Check labels, semantic controls, keyboard navigation, contrast and XSS.
New routes, forms, handlers or API interactions require actual browser tests with
positive and negative assertions. Prefer role/name or test-id selectors, mock only
external dependencies, capture console errors and screenshots on failure, bounded
condition waits and guaranteed cleanup. Target approved local synthetic endpoints.
Pure CSS/markup still needs relevant visual/accessibility checks; static checks alone
are not proof of appearance. If unavailable, report not tested rather than silently
waiving the criterion. CLI Playwright is an option only when already available;
Hermes browser tools depend on the actual session. No implicit container isolation.
