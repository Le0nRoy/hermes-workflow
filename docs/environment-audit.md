# Аудит Hermes, моделей и Kanban

Дата обследования: 2026-10-14, около 22:35–22:40 +04:00. Задача `t_2e69fee5`, доска `hermes-workflow`.

## Итог

Hermes установлен; единственный обнаруженный профиль `default` работает через локальный CLIProxyAPI (`pool`). Kanban уже исполняет эту задачу: запись claim/spawn и текущий worker подтверждены. Это не означает готовность отказоустойчивого контура для клиентской работы.

Основные ограничения: общий каталог без первого Git-коммита, отсутствие явно заданного лимита параллелизма и лимита времени карточек, не проверенные квоты/биллинг прокси, неподтверждённое восстановление worker после перезапуска. Claude-подписку нельзя считать автоматически доступным бюджетом Hermes. Для следующего этапа предлагается последовательный пилот с отдельным решением владельца о провайдере и правах; настройки в этом аудите не менялись.

## Метод и границы

Прочитаны AGENTS.md, README.md, docs/session-handoff.md, исходный manifest карточек, индекс второго мозга и релевантные заметки об агентных процессах и ресурсах. Личный контекст сюда не копируется. Использован `hermes-agent` версии 3.2.0 с references/providers-and-models.md и references/background-systems.md.

Проверки: CLI версии и справки, выбранные безопасные поля `hermes config get`, metadata проекта/доски, systemd properties, loopback listener, чтение SQLite с `-readonly`, исходники установленного диспетчера и provider plugin, официальные веб-страницы. Базы, сырые чаты, секреты и credential-файлы не копировались; `.env`, `auth.json` и токены не открывались. Дополнительные inference-запросы, OAuth, refresh, покупки, установка/обновление, переключение провайдера, рестарты, публикации и новые workers не запускались.

Read-only относится к обследуемой конфигурации и сервисам. Допустимые записи этой работы: данный отчёт, heartbeat и завершение собственной карточки; браузер и CLI могут создавать обычные runtime/cache данные. Доска меняется параллельно, поэтому ниже приведён датированный снимок, а не второе хранилище статусов.

## Подтверждённая среда

| Объект | Наблюдение |
|---|---|
| Tool host | `primary-host`, Linux `7.2.9-arch1-1`, x86_64 |
| Workspace | `${HERMES_WORKFLOW_ROOT}` |
| Git проекта | `chore/bootstrap`, unborn HEAD: первого коммита нет; remote не выведены |
| Исходные файлы | Все существующие файлы каркаса untracked; не изменялись |
| Hermes | `v0.21.6+730.g97a9ae8 (2026.9.24)`, stable, git-install |
| Hermes source | `${HERMES_HOME}/hermes-agent`, commit `97a9ae8ee55d31bebce49f1fb6b5ef775323976a`; `git status --short` пуст |
| Runtime версии | Python `3.14.7`, OpenAI SDK `2.24.0` из `hermes --version` |
| Профили | `hermes profile list`: только `default`; default model `gpt-6-sol`, gateway running |
| Активный home | `${HERMES_HOME}` |
| Локальные CLI | `codex-cli 0.162.1`, Claude Code `2.1.296`, оба доступны в PATH |
| Terminal backend | `local`: команды выполняются на хосте, не в Docker sandbox |
| Approval policy | `approvals.single_query_mode: deny` |
| Бюджет агента | `agent.max_turns: 150`; `agent.max_iterations` не задан |

Команда `hostname` отсутствует; имя хоста подтверждено `uname -n`. Ошибка `git rev-parse HEAD` ожидаема для репозитория без коммитов, а не признак потери существующей истории. Worktree-пилот нельзя считать готовым до согласованного первого коммита. Для аудита сохранена существующая немагистральная ветка, без commit/push и без переключения общей рабочей директории.

## Подключения моделей

| Уровень | Подтверждённое состояние |
|---|---|
| Профиль default | provider `pool`, model `gpt-6-sol`, base URL `http://127.0.0.1:8317/v1` |
| Эта карточка | override provider `pool`, model `gpt-6-astra`; это не смена глобальной модели |
| Pool plugin | `~/.hermes/plugins/model-providers/pool/__init__.py`: `chat_completions`, `auth_type=api_key`, имя переменной `CLIPROXY_KEY` |
| Fallback chain Hermes | `fallback_providers: []`; legacy `fallback_model` не задан |
| Auxiliary | наблюдаемые задачи имеют provider `auto`, без явной отдельной модели/endpoint; background_review и title_generation enabled |
| Внешние CLI credentials | `auth.adopt_external_logins: true`; фактические логины и срок действия не проверялись |

Статический fallback-каталог plugin: `gpt-6-sol`, `gpt-6-astra`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.5`. Это каталог имён, не цепочка failover и не подтверждение текущей доступности моделей. Официальная страница Codex pricing сообщает retirement GPT-5.5 в ChatGPT/Codex 14 октября 2026; имеющийся catalog entry требует последующей проверки, но не удалялся.

Loopback endpoint отвечает HTTP 401 на GET `/v1/models` без ключа: процесс отвечает и требует аутентификацию на этом endpoint. Полный model discovery не выполнялся, чтобы не извлекать секрет. Текущий worker реально ведёт многошаговую сессию с tool calls через назначенный `pool`; это ограниченное подтверждение работающего основного пути, не независимый тест всей матрицы моделей, streaming, failover, стоимости или upstream-аккаунтов.

Прокси — локальный транспорт, а не доказательство локального inference. Название systemd unit «pool of ChatGPT/Claude subscriptions» не подтверждает подключённые аккаунты, действующие тарифы или разрешённость каждого маршрута. Внутренние fallback/rotation CLIProxyAPI не обследованы. `auxiliary.*=auto` также не означает отсутствие дополнительного расхода: компрессия, review и другие помощники могут вызывать модель отдельно.

## Сервисы и диспетчер

| Проверка | Результат |
|---|---|
| `hermes-gateway.service` | enabled, active/running, `Restart=always`, PID 1392455, `NRestarts=3` |
| `cliproxy.service` | enabled, active/running, `Restart=always`, PID 3618450, `NRestarts=1` |
| User linger | `Linger=yes` |
| Proxy listener | `127.0.0.1:8317`, процесс `cli-proxy-api`; в этой проверке не слушает `0.0.0.0:8317` |
| Worker этой карточки | PID 2493038, PPID 1106354, command `hermes` |
| Родитель worker | PID 1106354, PPID 1, command `hermes`; не совпадает с MainPID gateway unit |

Важно: enabled/running и `Restart=always` подтверждают supervision, но не успешность recovery-сценария. Причины исторических NRestarts не исследовались. Родитель текущего worker отличается от gateway unit: из этих данных нельзя приписать его запуск именно `hermes-gateway.service` или утверждать, что dispatcher единственный. `systemctl --user list-units --type=scope ... 'hermes-worker*'` не вернул scope. Чтение `/proc/.../cgroup` через read_file вернуло пустой результат (инструмент ориентируется на размер pseudo-file), поэтому принадлежность worker к cgroup и его выживание при restart не подтверждены. Не запускать второй dispatcher для «исправления» без отдельной диагностики.

Наблюдаемая resolved-конфигурация Kanban:

- `dispatch_in_gateway: true`, `notify_in_gateway: true`, `review_dispatch: true`.
- `dispatch_interval_seconds: 60`, `failure_limit: 2`.
- `dispatch_stale_timeout_seconds: 14400`, `reconcile_orphans: true`.
- `max_in_progress: null`, `max_in_progress_per_profile: null`.
- `dispatch_profiles: null` в resolved выводе; этот вывод не различает отсутствующий ключ и явно заданный null. По актуальной документации явный null fail-closed, отсутствие ключа разрешает существующие профили. Текущий факт запуска подтверждён отдельно; политику live-процесса нельзя вывести только из этого поля.
- `auto_decompose: true`, `auto_decompose_per_tick: 3`; triage может вызывать LLM и создавать задачи.
- `orchestrator_profile` и `default_assignee` пустые.
- `worker_log_rotate_bytes: 2097152`, `worker_log_backup_count: 1`.

Обнаружено расхождение документации и установленного кода: веб-таблица описывает unset max_in_progress как unlimited, но установленный `hermes_cli/kanban_db_dispatch.py:1835–1857` вычисляет memory-derived cap с границами 2–8. `gateway/kanban_watchers_dispatcher.py:64–71` использует этот resolver. `free -m` показал total 15369 MiB; расчёт по формуле выполнен SQLite и дал 8. Это вывод по установленному коду и текущей памяти, не прочитанное live-значение давно запущенного dispatcher. Явного ограничения до одного worker нет; автоматически считать работу последовательной нельзя.

## Kanban и привязка проекта

Авторитетное состояние: `${HERMES_HOME}/kanban/boards/hermes-workflow/kanban.db`. Переменные worker `HERMES_KANBAN_DB` и `HERMES_KANBAN_BOARD` указывают именно на эту доску, а не на legacy `~/.hermes/kanban.db`.

- SQLite `PRAGMA quick_check`: `ok`.
- На снимке: 12 карточек, 12 уникальных ID; 10 blocked, 1 running (этот аудит), 1 todo (`t_93841548`).
- Все 12 ID совпали с `docs/kanban-tasks.json`, лишних ID нет. В БД и manifest по 15 зависимостей; двустороннее сравнение SQL EXCEPT подтвердило `missing_edges=0`, `extra_edges=0`.
- Все карточки: assignee `default`, workspace kind `dir`; project_id и max_runtime_seconds в существующих строках пустые. Общая директория предполагает последовательных авторов, не безопасный параллелизм.
- События собственной карточки: claimed/spawned 18:34:57 UTC и последующие heartbeat. Это реальный запуск, не только конфигурация.
- `t_93841548` сначала наблюдалась blocked, затем событие `unblocked` в 18:35:35 UTC и model/reasoning overrides в 18:35:57 UTC. Эти изменения сделаны не этим аудитом. Пока родитель не завершён, она todo; после завершения аудита может автоматически стартовать. Остальной backlog здесь не разблокировался.
- Board metadata: `project_id=p_5118b7e2`, default_workdir равен workspace.
- `hermes project show p_5118b7e2`: проект `hermes`, display name `Hermes`, primary folder равен workspace. Привязка доски к проекту теперь подтверждена metadata и CLI, вопреки исходному handoff, где она ещё считалась отдельной операцией. UI Desktop не проверялся.

Исходный docs/session-handoff.md — историческая точка старта: утверждения «все blocked» и «привязка не подтверждена» уже не описывают живой снимок. Manifest остаётся списком ID/зависимостей, не зеркалом статусов. В рамках аудита эти чужие файлы не переписывались.

## Подписки: поддержка и ограничения

Официальные страницы открыты 2026-10-14. Техническая поддержка в Hermes не равна разрешению поставщика или включённой квоте конкретного аккаунта.

### ChatGPT / Codex

1. Hermes документирует провайдер `openai-codex`, ChatGPT OAuth (device flow либо browser PKCE), собственный auth store и возможность импорта Codex CLI login. Установка Codex CLI для прямого провайдера не требуется. В этом аудите логин/импорт не выполнялся.
2. OpenAI Codex pricing подтверждает включение Codex в ChatGPT планы, в том числе Plus; квоты зависят от модели, контекста и задачи, могут быть общими с другими агентными функциями. API billing отделён от subscription usage. Нельзя обещать фиксированное число задач или отсутствие перерасхода без проверки account dashboard.
3. OpenAI authentication docs рекомендуют API-key authentication для programmatic Codex CLI workflows, например CI/CD; enterprise access tokens описаны отдельно. Наличие подписочного login не даёт автоматически доказанного SLA/разрешения на произвольную unattended-ферму через сторонний proxy.
4. Hermes прямо отмечает, что точная семантика потребления ChatGPT-квоты в его интеграции не полностью документирована. Поэтому прямой `openai-codex` — кандидат на согласованный ограниченный пилот, а не уже проверенный бесплатный production-путь.

### Claude

1. Официальный unmodified Claude Code с собственным пользовательским subscription login — явно описанный Anthropic путь. CLI установлен; login и квота не проверялись.
2. Текущие Hermes docs говорят: Claude Pro не поддерживается их OAuth-путём; Max требует purchased extra usage credits, базовая Max allowance не используется. Это не соответствует цели «только имеющиеся включённые квоты» и само по себе не является разрешением Anthropic на стороннюю интеграцию.
3. Anthropic legal/compliance описывает OAuth как поддержку обычного использования Claude Code и native applications; запрещает third-party разработчикам предлагать Claude.ai login и промежуточную маршрутизацию через Free/Pro/Max credentials для пользователей. Consumer Terms запрещают автоматизированный доступ, кроме API-key или явно разрешённых случаев. Отдельно разрешён вход конечного пользователя в неизменённый Claude Code. Не трактовать это как универсальный запрет самого CLI, но и не переносить разрешение на CLIProxyAPI.
4. Для прямого внешнего Claude API используется API key с отдельной оплатой; не подключать без согласия. Существующий pool не менялся и не отключался; законность и биллинг его Claude-маршрута не подтверждены. Наличие технически работающего обходного маршрута не считать compliance-доказательством.

## Варианты минимального контура — предложения, не решения

### A. Последовательный пилот на существующей инфраструктуре

Одна согласованная карточка, один writer в общей директории, один независимый review/human gate; единственный источник статуса — Kanban. Перед пилотом владелец подтверждает допустимый model route, квоту и отсутствие нежелательных платных fallback. Pool допустимо оценивать технически, но его непроверенные upstream-условия не скрывать. Не запускать параллельные карточки только потому, что профиль один.

### B. Прямой Hermes → openai-codex

После одобрения — штатный пользовательский OAuth, без переноса refresh tokens вручную и без одновременных владельцев обновления одного grant. Выполнить отдельно небольшой completion/tool-call тест, проверить учёт квоты, затем одну API/UI-задачу с негативными кейсами и детерминированными тестами. По возможности сначала run-scoped выбор, не глобальное переключение default. Для постоянной headless-эксплуатации отдельно согласовать условия и бюджет.

### C. Официальные CLI под контролем владельца

Codex / неизменённый Claude Code для работы по подпискам, Kanban — учёт результата и handoff; без извлечения Claude OAuth в generic proxy. Ручной ограниченный запуск — более консервативный старт, чем новая unattended-интеграция. Перед автоматизацией назначить владельца полного запуска тестов, восстановления, review; push/PR остаются отдельным согласованием. Не вводить вторую обязательную очередь Tortuga-AI поверх тех же задач.

Общие предварительные решения для t_93841548:

- Явно согласовать concurrency (предложение: 1), runtime/quota limits и stop-condition; не применять автоматически глобально к другим работам.
- Согласовать первый Git-коммит, затем worktrees перед параллелизмом. Профиль/worktree организационно разделяют работу, но не права OS и credentials.
- Для клиентских данных отдельно проверить OS/container, mounts, network и доступ к секретам. Текущий local backend с общим UID не подтверждает security isolation.
- Проверить, какой процесс владеет dispatch, и восстановление worker при restart/квоте в отдельной разрешённой задаче. Не считать `Restart=always` таким тестом.
- Планировать резервное копирование внешней SQLite отдельно от Git; наличие бэкапа и restore не проверены.

## Проверки, ошибки инструментов и остаточные ограничения

Успешно выполнены реальные read-only команды: version/profile/config/project queries, git status/commit install, systemd show/is-enabled, listener/401 probe, SQLite count/manifest ID и edge comparison/quick_check, чтение dispatcher/plugin source. `git diff --no-index --check /dev/null docs/environment-audit.md` прошёл без замечаний; конечный git status содержит исходные untracked-файлы и новый отчёт. Никакая тестовая API/UI-система этим аудитом не создавалась: это исследование среды, а не выполнение следующего этапа.

Два вызова `python -c` и один `execute_code` были заблокированы approval policy unattended-run; они не исполнились. Политика не ослаблялась, обход произвольного исполнения не делался: использованы штатные CLI, SQLite read-only и browser для публичных источников. `web_extract` недоступен с выбранным search-only backend DDGS; индекс получен curl, страницы — browser DOM. Help Center OpenAI по статье 11369540 дважды вернул пустой текст; выводы основаны на доступных официальных developers.openai.com/auth и /pricing, не на непрочитанной статье.

Не проверены: реальный тариф/оставшаяся квота аккаунтов, содержимое auth stores, оплаченные credits, pool upstream routes/полный model catalog, автоматическое восстановление и quota exhaustion, единственность dispatcher, доставка уведомлений, security isolation, backup restore, реальная стоимость текущей сессии. Документы описывают текущий upstream; при расхождении поведение установленной версии сверялось с её кодом, но код на диске не доказывает версию уже запущенного долгоживущего процесса.

## Источники

- https://hermes-agent.nousresearch.com/docs/llms.txt — актуальная карта документации.
- https://hermes-agent.nousresearch.com/docs/integrations/providers — OAuth, auxiliary routing, subscription caveats.
- https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban — lifecycle, dispatch, workspaces, notifications, recovery.
- https://developers.openai.com/codex/auth — subscription/API authentication, programmatic usage.
- https://developers.openai.com/codex/pricing — plan inclusion, shared limits, credits, retirement notice.
- https://code.claude.com/docs/en/legal-and-compliance — native CLI и authentication/credential-use boundaries.
- https://www.anthropic.com/legal/consumer-terms — раздел 3; опубликованная effective date 2025-10-08.
- Установленный commit Hermes `97a9ae8ee55d31bebce49f1fb6b5ef775323976a`: `hermes_cli/kanban_db_dispatch.py:1811–1857`, `gateway/kanban_watchers_dispatcher.py:50–117`.
- Локальный plugin: `~/.hermes/plugins/model-providers/pool/__init__.py:4–17`.

Результат предназначен для следующей существующей карточки `t_93841548` — согласование архитектуры. Аудит не утверждает архитектурные решения за владельца и не запускает её внедрение.
