# GitHub ↔ Hermes: A/B двух оркестраторов

Карточка: `t_0957877a`. Исследование: 2026-10-16, около 23:06 +04. **Статус: проект решения, не утверждённая и не развёрнутая интеграция.** Карточка не закрывается. Разрешённый результат этой работы — только этот новый документ; dispatch, изменения конфигурации, сервисов, GitHub и коммиты не выполняются.

## 1. Вывод и рекомендация

Использовать небольшой детерминированный **Hermes orchestration service + CLI adapter** поверх существующего Kanban lifecycle. Bridge оставить общим проверяющим ingress/router, владельцем штатных Tortuga runs и временным branch coordinator; для Hermes runs он **не** владеет очередью исполнения, retry, timeout или восстановлением. Постепенно переносить lifecycle в Hermes, а не навсегда запускать Hermes как ещё один контейнер под `_monitor_container` Tortuga.

Прямое подключение второго webhook к тем же labels сейчас небезопасно: Tortuga уже имеет webhook dispatch, label reconciliation, очередь, retries, loop и recovery; его dedup fail-open, selector `agent:hermes` в изученном контракте не предусмотрен. У Hermes есть durable Kanban/atomic claim и нужные CLI, но **нет доказанного готового end-to-end контракта ownership + atomic cancel без redispatch + совместных branch locks**. Поэтому рекомендация — направление реализации с обязательными доработками и лабораторией, не «достаточно написать shell wrapper».

Приоритет: общий admission/ownership contract → read-only shadow → изолированные failure tests → один вручную выбранный research → implement с полным runner contract → расширение. Не включать unattended sync/dispatch до прохождения gates ниже. Полнота списка установок GitHub App не установлена: локальные клоны перечислены с доказательством в §4, а live API inventory заблокирован разрешением.

## 2. Подтверждённые решения и границы

Основания: текущие указания владельца; `hermes kanban --board hermes-workflow show t_0957877a --json`, комментарии `default` с `created_at=1792053102` и `1792175164`; `AGENTS.md:10–26`; `docs/architecture.md:33–41,90–113,164–175`. Прочитаны README, architecture, card-operating-model-proposal, INDEX второго мозга и skill hermes-agent с references webhooks/background-systems/desktop-plugins. Последующий iteration/supervisor дизайн в `docs/card-operating-model-proposal.md:8–36` **не принят**; принято лишь «операторский чат + Kanban registry». Новый документ не утверждает автоматически остальные предложения.

- `agent:hermes` вместе с `agent:research` или `agent:implement` выбирает Hermes. Без selector обычный Tortuga; отсутствие label само по себе не команда старта.
- Selector ставится человеком явно на **каждом executable issue/PR**, без наследования milestone/meta/parent/issue→PR. Только research/implement; прочее с selector — явный unsupported, **без fallback**.
- Owner фиксируется при создании run. Смена selector влияет только на последующий run, не переносит уже queued/active/recovery work. Stop — существующий bridge UX с маршрутизацией записанному owner.
- GitHub comments issue/PR — межэтапный контекст. Start, существенный blocker, final, PR/artifact links пишутся обратно; сырые логи/admin diagnostics не публикуются.
- Одна Kanban execution card на action/run допустима; отдельная issue-карточка необязательна. Issue closure остаётся merge PR automation, не `kanban_complete`.
- Крупная работа: decomposition → отдельные части → integration branch → проверка комбинации → ручной merge в main как acceptance. Meta issue опционален, delivery invariant обязателен. Пока integration branches контролирует bridge.
- Scope выбирается вручную, массовый импорт не нужен для первого пилота. Не создавать вторую обязательную очередь одной работы.
- Read-only этой задачи не разрешает будущие push/PR, новые credentials, расходы, деплой, restart, изменение конфигурации или прав. Профиль/worktree не являются sandbox.

Снимок карточки при чтении: `triage`, runs пусты, дети `t_d939d3e8`, `t_f7c5c60d`; состояния не менялись. Triage не является доказанным human gate: auto-decomposition нужно учитывать отдельно. Этот документ не запускает дочерние задачи.

## 3. Проверенная база и ссылки на код

Для кратких ссылок ниже:

- `T/` = `${TORTUGA_AI_ROOT}/`.
- `H/` = `${HERMES_HOME}/hermes-agent/`.
- `R` = `T/agent-bridge/agent_runner.py`; `M` = `T/agent-bridge/main.py`; `K` = `H/hermes_cli/kanban_db.py`; `D` = `H/hermes_cli/kanban_db_dispatch.py`.

Проверено CLI: Hermes `v0.21.6+730.g97a9ae8`, установленный revision `97a9ae8ee55d31bebce49f1fb6b5ef775323976a`. Tortuga checkout: `6fcde6883a26d94563ffe6a781bec8f7719b0e1d`, ветка `agent/feature-778`, без показанных локальных изменений. SHA-256 **содержимого** `main.py`, `agent_runner.py`, `models.py` в запущенном `agent-bridge:/app` совпал с checkout. Это связывает изученные главные файлы с live deployment, но не доказывает совпадение всех зависимостей/config.

Workspace документа: unborn feature-ветка `feat/recovery-lab-t_484bba3b`, существующие untracked `.gitignore`, AGENTS, README, docs, experiments, skills, tests. HEAD этого workspace отсутствует; чужие файлы и ветка сохранены. Reproducible A/B baseline требует отдельного разрешённого коммита в пилотном репозитории, не скрытого bootstrap commit здесь.

### 3.1 Tortuga: реальные entrypoints и владельцы lifecycle

| Область | Проверенный код | Следствие |
|---|---|---|
| Ingress/auth | `M:439–458,894–925`; `R:2298–2370` | Сохранить проверку webhook signature и права sender; selector не расширяет права |
| Issue/PR triggers | `M:596–718,856–951` | PR labels приходят также как issue events; issues-handler отбрасывает PR (`903–907`) |
| Run contract | `T/agent-bridge/models.py:15–34,45–79`; `R:12308–12396` | DispatchArgs хранит event/action/repo/number/milestone, **не owner/selector/repo ID**; добавить поля и проверку replay |
| Dedup | `R:2766–2836` | Redis SET NX с TTL по repo/number/task; при ошибке Redis пропускает dispatch (`2775–2785`). Это не fencing для двух оркестраторов |
| Reconciliation | `R:2524–2689` | Повторно читает action label и вызывает dispatch; selector/owner должны проверяться и здесь, не только в webhook |
| Queue/retry | `R:7698–7805,8217–8350,11664–11768` | Retry получает новый Tortuga run UUID; очередь tier-0/tier-1, отдельные capacity/transient/usage-limit пути. Hermes нельзя одновременно положить сюда и в Kanban |
| Recovery | `R:10266` и следующие recovery/orphan helpers; `10389`, `11029` | Есть отдельные container/worktree/queue/loop recovery paths; маршрутизации только в main.py недостаточно |
| Stop UX | `M:722–818,960–1028`; `R:2857–2956` | Удаление trigger label человеком останавливает active/cancel queued; bot self-removal игнорируется. Сейчас stop адресован контейнеру `agent-runner-{run_id}`, не Hermes |
| Loop/CI | `M:601–636,740–769,820–854,1057` и далее; `R:4037` | Loop и synchronize/check-suite могут добавлять action labels автоматически. В Hermes v1 запрещены, не должны обходить selector/unsupported gate |
| Integration | `R:12720–12824,12844–12897,13002`; `models.py:66–73` | Есть sibling/blocker guard, `agent/feature-{parent}`, branch locks и отдельный PR base; сохранить как общий contract |
| Closure | `M:544–594`; `R:5702–5723` | Sub-PR merge в `agent/feature-*` закрывает referenced issues; последний sibling может добавить `agent:review` integration PR. Не дублировать закрытие из Kanban |
| Runner | `T/agent-runner/run.sh:322–452`; `implement_loop.py:135–150,298–369,442–563` | Не один prompt: Claude session → полный test target → bounded fix → push → draft PR/update и Local verification. Hermes этого автоматически не наследует |

Найденный дополнительный риск inventory: `_list_installation_repos` документирует `None` при неполной ошибке (`R:1624–1626`), но при failed repositories-page делает `break` (`1693–1698`) и в конце возвращает частичный result (`1710`). Будущий sync не должен трактовать такой снимок как полный и удалять отсутствующие записи. Исправление здесь не выполнялось.

### 3.2 Hermes: какие интерфейсы действительно доступны

Уровни проверки: **CLI** — команда `--help` реально выполнена; **код** — implementation прочитан/найден; **HTTP** — безопасный GET выполнен; ни один уровень сам по себе не end-to-end тест.

| Интерфейс | Проверка и ограничения |
|---|---|
| `hermes chat --query-file PATH --oneshot --format stream-json --max-turns N --run-budget SECONDS --in DIR` | CLI доступен; `H/hermes_cli/_parser.py:264,292`; `H/hermes_cli/stream_json.py:1–5,18–30,37–100`; init/text/tool/result JSONL и session ID есть в коде. Модель не запускалась. Использовать argv, не shell interpolation внешнего текста |
| `hermes -z ... --usage-file PATH` | CLI доступен, но **approvals auto-bypassed**: `H/hermes_cli/oneshot.py:1–4,215–250`. Не выбирать как безопасный default. `chat --oneshot` не считать sandbox: effective deny и subprocess/tool children проверить отдельно |
| Kanban create/show/runs/block/reclaim/dispatch | `--help` реально выполнен; exact `show` карточки выполнен. Create имеет board, workspace, branch, project, idempotency-key, max-runtime, max-retries, initial-status, completion-contract. State-changing команды **не запускались** |
| Atomic task claim | `K:2149–2208`: CAS + run row в транзакции. Run identity = board + task + integer run ID, не только task ID |
| Create idempotency | `K:1250–1259`: lookup **до** write transaction; комментарий прямо допускает concurrent duplicate creation. `--idempotency-key` — не достаточный глобальный unique lock |
| Runtime/recovery | `D:443–607,648–733,1525–1572,1953`; `D:2831–2960` | Spawn передаёт task/board/run/claim/workspace env, PID; runtime timeout переочередяет, rate-limit может не считать failure. `max-retries=1` не универсальный hard cap всех повторов |
| Reclaim/terminate | `K:2493–2526`; `H/plugins/kanban/dashboard/plugin_api.py:985–999` | Reclaim возвращает task в retry phase и сбрасывает failure budget. Это **не cancel-and-park**. CLI reclaim, затем block оставляет окно redispatch; POST terminate использует тот же reclaim. Не использовать такую пару как доказанный stop |
| Typed block | `K:3143–3234` | `needs_input/capability` sticky; dependency может стать todo; block закрывает claim, но сам по себе не подтверждает остановку процесса. Не заменяет atomic cancellation |
| Plugins Python | `H/hermes_cli/plugins.py:156–188,230,633,933` | Есть PluginContext, register_cli_command/register_hook, kanban claimed/completed/blocked/spawned/exited/dispatch_tick observers. Их return игнорируется; tick после lock. **Это не preclaim admission veto** |
| Desktop plugin | Официальный SDK и skill reference | UI/client, не durable lifecycle owner. Закрытый Desktop не должен останавливать orchestration; frontend plugin не заменяет daemon |
| Native webhook | `H/gateway/platforms/webhook.py:226–228,336–365,526,652–682,769` | HMAC/GitHub delivery header есть; seen-deliveries — process dict с TTL 3600. Нельзя считать durable дедупом после restart; prompt route не ownership router |
| HTTP run API | `H/gateway/platforms/api_server_runs.py:213–246,638–730,1253–1274`; `api_server_run_idempotency.py:53–100` | `/v1/runs`, status/events/stop, Idempotency-Key реализованы; durable store может fallback в memory. Stop отвечает `stopping`, не гарантией, что все effects прекращены. Для текущего хоста работающий API endpoint не подтверждён |
| Native dispatcher | `H/gateway/kanban_watchers_dispatcher.py:1–5,47–80`; `D:1953,2831` | Переиспользовать existing gateway single-writer; не запускать `kanban daemon`/второй `dispatch` loop |

Live endpoints: bridge `GET http://127.0.0.1:8765/health` → 200, status ok. На стандартных 9119/8644 connection failed. `hermes serve --status` и `ss -ltnp` обнаружили **реальный** loopback serve на `127.0.0.1:38941`; GET `/api/plugins/kanban/inspect?board=hermes-workflow` → **401**, `/health` и `/v1/capabilities` → **404**. Следовательно backend reachable, но доступа к Kanban HTTP без auth нет, а serve dashboard не тот же API-server adapter. Не читать SSH token files и не обходить 401. Новый listener/route не включался.

Значимый telemetry defect для дизайна: `stream_json.py:88–90` превращает missing token fields в 0. Поэтому один JSONL result недостаточен для требования «unknown не 0» и не доказывает покрытие auxiliary/delegated calls.

## 4. Репозитории: доказательства и предел полноты

Read-only `docker exec agent-bridge python -c ...` перечислил каталоги `/repos/<owner>/<repo>/.git`. Получены семь локальных clone paths:

| Локальный клон | Mapping-предложение |
|---|---|
| `Le0nRoy/AI-Wrapper` | Существующая доска `ai-wrapper` из требования карточки; проверить binding перед импортом. Submodule в chezmoi не перемещать |
| `Le0nRoy/Tortuga-AI` | Отдельная repo identity; board определить проверкой existing registry |
| `Le0nRoy/Tortuga-Infra` | То же; не объединять с Tortuga-AI по owner |
| `Le0nRoy/Tortuga-Library-Index` | То же |
| `Le0nRoy/bank_sms_tracker` | То же |
| `Le0nRoy/minecraft_server` | То же |
| `Le0nRoy/my_linux_configs` | То же; наличие AI-Wrapper submodule не означает одну execution scope |

Доказательство происхождения: Docker inspect вывел только mounts metadata; `/repos` смонтирован из volume `tortuga_agent_repos`. Поведение populate/sync: `R:1501–1544,1617–1710`; install/add/remove handlers `M:464–503`. **Клоны — свидетельство локальной регистрации/кэширования, не доказательство текущего полного App installation access** и не отдельное разрешение запуска.

Проверка доступа: в remote текущего Tortuga checkout нет embedded token; `gh api installation/repositories` недоступен (exit 4). Следующая попытка read-only GET `/installation/repositories` существующим credential из bridge clone была отклонена approval timeout, **команда не исполнилась и не повторялась**. Новый token не выпускался, credentials не выводились, remote не менялся. Полный authoritative список подключённых repos остаётся **unknown**; не выдавать семь клонов за total App repositories.

После отдельного разрешения inventory должен: GET `/app/installations` с App identity, для **каждой** installation постранично GET `/installation/repositories` с разрешённым installation credential; сохранять только installation/repo IDs и имена; dedupe по numeric repo ID; проверить `total_count`, pagination/Link и полноту каждой страницы. Installation token показывает лишь свою installation, не все установки App. Любая 401/403/timeout/неполная страница → incomplete, без удаления mapping. Прямой вызов `_list_installation_repos()` здесь не используется: он выпускает tokens и возвращает секреты в values.

## 5. CLI adapter, отдельный service или plugin

| Вариант | Что даёт | Почему не достаточно / стоимость |
|---|---|---|
| Разовый CLI adapter/script | Быстрый bounded запуск, JSONL/session, argv safety, локальный preflight | Сам не хранит ownership/outbox/cancel/recovery; если bridge ретраит его как worker, это тест **исполнителя**, не A/B lifecycle |
| **Service + тонкий CLI adapter, recommended** | Durable admission ledger и outbox, versioned protocol, health, native Hermes lifecycle; процессы не зависят от Desktop; легко shadow/rollback | Требует общих gates в bridge и узких безопасных расширений Hermes. Не добавлять собственную конкурирующую worker queue: execution/retry остаются Kanban |
| Python Hermes plugin | Удобно bundle tools/hooks/telemetry, profile-scoped package | Observers post-commit нельзя превратить в veto; crash/plugin exception не должен разрешать запуск. Нужен тот же durable contract; теснее связь с host. Позже оправдан для usage attribution/UI, не обязателен первым |
| Desktop-only plugin | Видимость mapping, кнопки/вопросы оператора | Не background authority. Не выбирать владельцем lifecycle |
| HTTP `/v1/runs` вместо CLI | Versioned async protocol, status/events/stop, idempotency | Реализован в установленном source, но live endpoint/auth/capabilities не подтверждены; run API не решает GitHub mapping/branches. Альтернатива после отдельной проверки, не fallback при отказе CLI |

**Минимальность не означает zero code changes.** В текущих интерфейсах нет доказанного безопасного native admission veto и atomic stop-and-park. До их реализации разрешены документация, shadow и лаборатория, но не unattended B. Plugin hooks можно использовать как ускоряющие уведомления, не как единственный durable journal; после restart догонять события по cursor.

## 6. Предлагаемый протокол A/B: один owner на run

Всё ниже — **новый contract**, а не существующие endpoints. Имена операций `Admit/Get/Cancel/Ack/BranchPrepare/Publish` логические; реализованность не заявляется.

### 6.1 Identity и durable admission, без второй очереди

Общий ingress остаётся один: проверяет HMAC, sender permission, repo allowlist, human scope/action. Перед любым spawn создаёт admission record в одном durable store с транзакционными unique constraints; store — журнал маршрутизации и effect/outbox receipts, **не очередь исполнения**. Для A он ссылается на native bridge queue/run; для B — только native Hermes board/task/runs. Не хранить здесь вторую изменяемую копию worker state; source owner возвращает authoritative state.

Минимальные поля записи:

- `schema_version`, `github_host`, numeric `repository_id`, `issue_node_id`/PR node ID, number, kind и URL; repo full_name — обновляемый locator, не primary key.
- `request_id` — immutable action invocation; `delivery_id` — envelope GitHub, плюс event/action/authorized actor и безопасный payload digest. Одна delivery может породить максимум один admission по `(delivery_id, object_id, action)`.
- `owner = tortuga | hermes`, selector snapshot, action snapshot, scope/permissions version, `admitted_at`, `request_generation`; `owner_epoch`/fencing token. Owner immutable до terminal.
- `logical_run_id` — одна разрешённая работа; `attempt_id` и native execution run IDs — отдельные. Повтор не меняет owner и не становится новым label request.
- base/head SHA, allowed branch+PR base, project/board/task mapping, model/provider/skill revisions, limits, context comment IDs/digest, cancellation tombstone, monotonic lifecycle version, outbox/effect receipts. Секретов и raw prompt/log здесь нет.

Unique active admission по `(repository_id, object_id, action)`; отдельный shared branch/writer lock предотвращает implement+review конфликт разных объектов/owners. Пилот консервативно один writer на repo, с учётом интерактивной работы. Локальные лимиты каждого оркестратора не заменяют общий lock.

**Отказ ledger/lock — fail closed до публикации/старта**, включая A на общей границе. Нынешнее `_acquire_dedup_lock` fail-open для нового контура неприемлемо. После TTL истечения не отдавать ownership новому worker лишь по времени: проверить процесс fingerprint/native run и effects; при неопределённости `recovery_unknown` + ручное решение. Fencing проверяется перед spawn, retry и каждым publish/branch effect. Произвольный shell push не является fenced: либо scoped broker publication, либо в пилоте credentials на запись только у publisher, не LLM worker.

### 6.2 Routing и порядок labels

1. Сначала selector, затем action — рекомендуемый human UX. Добавление одного selector не запускает работу. Если action уже запустил A, последующее добавление selector не мигрирует этот run.
2. Ingress читает актуальные labels при admission, фиксирует owner; при API ambiguity — blocked, не default-A. Использует object revision/context snapshot; запоздалые deliveries не могут откатить более новый terminal/cancel generation.
3. Action + selector → B только для research/implement. Unsupported (review/decompose/loop/прочее) → controlled rejection с actionable пояснением; никогда A fallback. Несколько одновременных action labels в пилоте → ambiguous/block до выбора, не параллельные действия.
4. Action без selector → A. Однотипный duplicate возвращает receipt existing admission без нового card/run/comment storm. PR issues.labeled и pull_request.labeled нормализуются к одному object identity.
5. Смена selector на queued/active work — только записать изменение metadata; **не cancel**, не новый admission. Retry/resume читает записанный owner, не latest label. Явное снятие action label человеком остаётся stop; bot lifecycle label mutation помечается origin/effect receipt и не считается human stop.
6. Reconciler различает **новый action request** и незавершённый/outbox/recovery существующего. Нельзя создавать бесконечно новый request от постоянно оставленного label. Нужны persistent consumption receipt и generation; новый run после terminal — явное re-add action/одобренная команда, не обычный sync.

Все producers обязаны идти через этот admission: webhook, reconcile, wait queue replay, retry scheduler, startup recovery, loop, CI/check-suite, synchronize. Для уже существующих до rollout runs при fence-cutover классифицировать **A** по native evidence; unknown старые entries парковать, не передавать B. Присутствие selector на старом run не переписывает owner.

### 6.3 Delivery и handshake B

1. Ingress атомарно фиксирует B ownership + outbox `Admit`; commit **до** ACK webhook. Crash до commit → redelivery безопасна; после commit → replay outbox, не повторный выбор owner.
2. Service принимает request ID + digest + fence, проверяет contract, durable mapping и cancellation. Один serialized creator на mapping key; не полагаться на non-atomic Kanban `--idempotency-key`. При uncertain create response сначала read back по mapping/key/marker; больше одной карточки → quarantine, не запускать ни одну автоматически.
3. Создаёт native execution card **blocked** с explicit board/workspace/completion contract/model/лимитами. Metadata import никогда не ready/triage. `initial-status running` не считать способом external-worker adoption: native initial state выводится в `H/hermes_cli/kanban_db_graph.py:25–51` и может стать ready.
4. `Ack` возвращает exact board/task + contract digest. Только native admission guard проверяет durable permit/fence/cancel/attempt budget непосредственно перед atomic claim. Вход в ready сам по себе не разрешение; нужен fail-closed guard всех automatic recovery paths. **Такого готового публичного veto интерфейса не найдено; требуется узкое расширение Hermes, до него B gated off.** Не запускать второй dispatcher в service.
5. Native Hermes создаёт task_run и worker. Service связывает события/run/session и пишет только effect/outbox state; не дублирует worker requeue. Bridge B не создаёт runner container, queue entry, semaphore retry или `_monitor_container`.
6. Worker не может менять routing grants/owner/iteration scope. Publisher подтверждает current fence и exact diff/tests/head; final write-back через idempotent outbox. DONE execution не закрывает GitHub issue и не означает ручной acceptance main.

### 6.4 Retry, timeout, stop и restart

| Ситуация | Единственный authority / правило |
|---|---|
| A queued/active/retry | Bridge native lifecycle, после проверки admission owner=A; Hermes только читает ссылку |
| B queued/active/retry | Hermes native lifecycle, с preclaim policy. Service не respawn-ит CLI и не ведёт параллельный retry timer |
| Retry transport | Отправитель повторяет **тот же** request/effect ID; это не новая execution attempt |
| B initial pilot | Один разрешённый attempt; максимум одна **ручная** следующая попытка после устранения причины, как A1-3. Все native recovery/timeout/quota paths должны проходить durable budget. Не предполагать, что `max-retries` покрывает quota |
| Quota/auth/timeout | Park + blocker + safe handoff; без provider fallback/вечных cooldown retries. Run budget CLI не заменяет process-tree/детерминированный test timeout |
| Delivery failure | Повторяется только comment/PR publication effect из сохранённого artifact, **не LLM работа**. Unknown POST outcome → read back marker/head перед повтором |
| Stop queued | Bridge UX → записанный owner → durable cancellation tombstone + revoke permit → remove native queued eligibility. Поздний Admit/Ack не снимает tombstone |
| Stop running | Tombstone/fence revocation до сигнала; owner прерывает worker и deterministic children; проверяет process fingerprint, отсутствие surviving writer, закрывает run и **паркует**, не ready. Final «stopped» лишь после подтверждения; иначе «stop requested/recovery unknown» |
| Completion ↔ stop race | CAS lifecycle version: если terminal effect committed до cancel — вернуть фактический результат; если cancel победил — reject late completion/publication и сохранить evidence отдельно |
| Controller restart | Read ownership/admission/outbox/native state. Живой worker — adopt/observe, не spawn; оконченный с artifact — delivery only; мёртвый без evidence — parked unknown, затем ручная новая attempt |
| Lease expiry/network partition | Нет автоматического owner transfer. Отсутствие heartbeat не равно смерти worker. Общий lock/fence и publisher должны исключить эффекты устаревшего worker |

**Stop blocker:** сегодняшние `reclaim`/HTTP terminate переочередяют; block не доказывает kill. Нужна атомарная native операция cancel-by-expected-run с persistent tombstone, удержанием claim до quiescence и sticky parked state, которую проверяют timeout/recovery/claim. `reclaim; block`, hooks после claim или глобальный `hermes pause` не годятся: первые race-prone, последний влияет на чужие работы. Это отдельная предлагаемая доработка, не готовая команда.

Rollback: запретить **новые** B admissions; уже B runs остаются B до stop/terminal. После quiescence следующая явно разрешённая action invocation без selector идёт A. Ни uninstall plugin, ни удаление selector не переводит активный B в A. Если B unavailable — ждать/stop по сохранённому owner, не fallback. Сохранить branch/artifact/mapping/receipts, не удалять worktree с WIP автоматически.

## 7. Branch coordination и обязанности runner

Первоначально bridge — единственный mutator shared integration branches/locks, независимо от run owner. Выделить **не-dispatching** capability contract: `BranchPrepare(request,fence,base_sha)` и `BranchRelease/PublishReceipt`; прямого безопасного публичного branch API в изученном bridge нет. Нельзя дергать `dispatch_agent` ради подготовки ветки: он уже клонирует/меняет labels/запускает lifecycle. До реализации capability — branch preparation вручную по отдельному разрешению и сериализация пилота, не скрытая автоматизация.

Contract на каждый run содержит base ref **и SHA**, work branch/ref, integration ref/SHA, PR base, allowed mutation set, lease/fence. Сохранить `agent/feature-{parent}` для существующих sub-issues. Если meta issue отсутствует, требуется новый явный stable `feature_id → integration branch` mapping и capability bridge; до его реализации не обещать без-meta автоматизацию. Не менять существующие epics и не генерировать фальшивый parent ради совместимости.

Части создают PR в integration branch, не main. Milestone/meta membership не dependency. Проверка очередности основана на prerequisites/blocked-by и интеграционных проверках, а не на открытом umbrella issue. После merge частей — full combined suite/CI на exact integration head; конфликт/changed base требует rebase и повторной проверки. Человек вручную merge integration PR в main; auto merge main запрещён. Снятие selector с integration PR может разрешить следующий review A только по обычному start gate; selector не наследуется от частей.

Распределение runner обязанностей для B (всё требует реализации/тестов, не обеспечивается prompt):

| Обязанность | Предлагаемый исполнитель |
|---|---|
| Research context/report | Hermes worker, GitHub comment IDs/links; без push |
| Targeted tests/local changes | Hermes implement worker в выделенном worktree |
| Полный repo test recipe, exit code/report, bounded fix | Детерминированный runner, под Hermes lifecycle; recipe из repo, не универсальный `make test-all` для всех семи проектов |
| Длинные тесты | Отдельно согласованный test process с timeout/resource caps/cancel/receipt, без LLM polling; не обходить 1800 секунд background-флагом |
| Commit/push/draft PR/update | Scoped publisher после разрешения, fence/head/scope/secret scan; idempotent PR по repo/head/base; сохранить Local verification |
| Review и окончательная приёмка | На v1 human, либо следующий явно A run без selector; Hermes review unsupported. Kanban review может auto-dispatch: не использовать его как human gate без проверки |
| Recovery/cleanup | Только owner; WIP сохранять; bridge branch coordinator не переисполняет worker |

## 8. Sync, mapping и разрешение конфликтов

Не делать GitHub и Kanban двумя равноправными writable master. Kanban — execution registry; GitHub — исходные требования/межэтапный публичный контекст и delivery acceptance. Durable mapping — корреляция, не третья user-facing очередь. Только один sync writer на repository identity, per-object serialization + durable cursor; webhook — ускоритель, bounded reconciliation — восстановление, не повторный dispatch.

| Поле | Owner / направление / конфликт |
|---|---|
| Numeric repo/node IDs, number, URL, rename | GitHub → mapping; full_name обновляется, stable identity сохраняется; permission loss не deletion |
| Issue/PR title/body/state, labels | GitHub → snapshot; изменения после admission не переписывают run scope. Существенное изменение → блок/новое согласование, не silent prompt update |
| Milestone/meta membership | GitHub → metadata; separate membership edges, **не** Kanban parent prerequisites |
| Blocked-by/prerequisites | Явные verified links → execution prerequisites; cross-board текст не выдавать за enforced edge. Закрытие GitHub issue не равно выполненной Kanban prerequisite без receipt |
| Routing owner/action/scope | Immutable admission; пользователь выбирает следующий action labels. Native latest labels не переписывают queued contract |
| Execution status, attempt history, heartbeat | Только owner native state → Kanban/display; A не создаёт dispatchable Hermes mirror; B не создаёт bridge execution queue |
| Questions/answers | Public relevant context в GitHub comments с stable question ID; operator chat может принять ответ, но он должен быть записан с источником/scope перед новой attempt. Ответ не автоматический resume grant |
| Start/block/final/artifact | Owner → outbox → GitHub comments; admin error details отдельно. Не публиковать внутренние run IDs/Redis paths/container names; непрозрачный marker для dedup без admin payload |
| PR/head/base/tests | GitHub + publisher receipts; remote read-back exact head/base и требуемых CI, не один exit 0 от CLI |
| Issue closure/deletion | Только existing merge process/GitHub; done/archive card никогда не closes issue. Deleted/unavailable object → tombstone/inaccessible, сохранить audit, не удалить активную работу |

Mapping cardinalities: repo → explicit project/board; issue/PR → 0..N action admissions; admission → ровно один owner и B execution card (для A достаточно external run reference); card → 1..N native attempts; attempt → sessions, calls, artifacts и effects. Структурная issue mirror card опциональна и всегда недиспетчеризуема; не создавать её как parent всех работ.

Comment sync: cursor по stable comment ID/update timestamp, pagination, edit/delete reconciliation и source hash. Не копировать raw logs/credentials. Bot-origin marker и effect receipts предотвращают feedback-loop от собственного write-back; неизвестные bot comments не считать human permission. Outbox хранит ожидаемый объект/тип/версию эффекта. На retry POST после timeout сначала искать marker и сверять content digest; при edit конфликте не затирать человеческий текст. PR update — только owned section, preserving human body; если head/base поменялись, publication блокируется до повторной проверки.

Импорт phase 1 только metadata, explicit blocked/local-only cards если нужны; предпочтительно сначала dry-run без создания. Полный импорт всех repos, создание boards/project bindings и cron reconciliation — отдельное разрешение. Никогда не switch global current board в service; каждую CLI операцию выполнять с `--board`.

## 9. Метрики A/B

Инфраструктурную надёжность сравнивать отдельно от качества Tortuga skills / make-feature / bulletproof, а не объединять их автоматически. A/B не означает одновременно запускать A и B на одном issue/branch: matched безопасные задачи или последовательные независимые worktrees от одинакового baseline, разные request IDs, но никогда две execution authorities одной invocation.

Обязательная attribution: repo/object/action/logical run/owner/attempt/board/task/native run/session/call. Зафиксировать требования, начальный SHA, model/provider/skill/runner revisions, routing/permissions policy, тесты, intervention и результат принятия.

- `clarification_requests`: уникальные question IDs, реально заданные человеку, включая разрешённые затраты/доступ; повторы одного вопроса не увеличивают счётчик. Отдельно `unresolved_final`: вопросы, не разрешённые к terminal/handoff. Различать продуктовые вопросы и approval gates.
- Input/output/cache-read/cache-write — все provider calls всех attempts, включая неуспешные, orchestrator/auxiliary/compression/judge/delegation. Cache semantics провайдера хранить явно: не складывать cache-read с input второй раз. Partial coverage → известная сумма + список unknown streams, **не полный нулевой расход**.
- CLI JSONL missing→0 нормализация требует raw usage/observer evidence или исправления provenance; одиночный 0 без coverage flag трактовать unknown. `--usage-file` имеет другой approval contract и не решение этой проблемы автоматически.
- `queue_time`: admitted → фактический start каждой attempt; суммировать отдельно backoff/resource wait. `active_time`: подтверждённые execution intervals, отдельно LLM/test/publish при наличии. `wall_time`: admission → terminal, включая ожидание человека. Параллельные вызовы не суммировать как wall. Restarts требуют durable timestamps; elapsed CLI — лишь process interval.
- Quota остаток и estimated cost — разные поля. Название provider/pool не доказывает оплату. Unknown не 0; новые расходы не разрешены. Первыми измерять zero-LLM fixtures и existing monitoring, не разворачивать второй mandatory dashboard.

## 10. Этапы, проверки и go/no-go

Ниже **план тестов**, не отчёт об их прохождении. Fixtures только в отдельно разрешённой лаборатории, без production restarts, настоящих секретов и live issues. До запуска согласовать baseline, route/бюджет, caps, время наблюдения и допуски; текущая работа их не запускает.

| Этап | Что сделать | Проверяемый exit criterion |
|---|---|---|
| E0 Контракт | Подтвердить этот дизайн; завершить authoritative repo inventory, mapping boards и credential scope; согласовать code changes | Один владелец полей/lifecycle, полный inventory либо явно ограниченный pilot scope |
| E1 Shadow | Read-only routing decisions на sanitized webhook fixtures/разрешённых snapshots, без card creation/dispatch/write-back | Матрица labels/order/PR dual events/unsupported даёт ожидаемый owner, 0 side effects |
| E2 Admission | Unique ledger/outbox; все bridge producers используют owner; B не bridge queue; fail closed | Concurrent duplicate/redelivery/restart выдаёт один admission/одну B card, не один «самый новый» duplicate |
| E3 Native policy | Hermes preclaim guard, all-path attempt budget, atomic cancel/park, publisher fencing; branch capability bridge | Stop/retry/recovery failures не создают второго writer/effect; нет окна reclaim→respawn |
| E4 Research pilot | Один manually scoped repo/object, public fixture, bounded route | Start/block/final GitHub read-back, контекст воспроизводим без private memory, метрики полны либо marked partial |
| E5 Implement pilot | Worktree/branch contract, полный recipe, push/draft PR только после разрешения | Correct PR base, exact-head tests/CI, delivery retry без нового LLM run, manual main acceptance |
| E6 Expansion/rollback | Увеличить scope по отдельному решению; deterministic reconcile; проверить drain | Active owners не мигрируют; новые B off, старые safe-stop/terminal, следующая invocation A |

Обязательные лабораторные кейсы:

1. Дубли одной delivery и разных deliveries одной invocation одновременно; PR issues+pull_request pair; concurrent Kanban creates. Один admission/card/worker, duplicate returns same receipt.
2. Selector добавлен/удалён после queue/start; research B → следующий implement A и наоборот; PR без selector не наследует issue. Retry старого run остаётся owner snapshot.
3. Unsupported review/decompose/loop с selector; stale CI/auto-review/synchronize; startup legacy queue. Ни одного скрытого A fallback/B unsupported worker.
4. Crash до/после ledger commit, create-card ACK, claim, spawn, artifact, push, PR POST, final-comment ACK. Recovery не делает второй эффект; ambiguous effects сначала read-back, иначе park.
5. Stop до Admit, queued, setup, active, tests, publish; повтор stop; stop↔complete; worker не реагирует на TERM, PID reused, partition. Tombstone survives restart, no new claim, подтверждена quiescence/либо honest unknown.
6. Redis/SQLite/permission failure, dedup TTL expiry, split controller, stale heartbeat с живым worker. Fail closed, не новый writer. Отдельно доказать native reclaim failure не отпускает работу опасно.
7. Timeout/quota/429/auth, native rate-limited path и max-retries; permit budget нельзя обойти requeue/reclaim. Никакого платного/provider fallback; manual attempt имеет новый ID и тот же owner.
8. Branch writer conflict A↔B, sub-PR в integration, stale base/head, конфликт merge, без-meta feature mapping. Совместный lock, correct target, full combined suite; main только человек.
9. Sync rename, deleted/inaccessible issue, paginated inventory partial failure, human comment edit, echo webhook, updated requirements. Нет удаления mapping/перезаписи human text/неожиданного dispatch.
10. Usage fixture с missing fields и auxiliary/delegation calls, повторными попытками и временем ожидания. Missing остаётся unknown; clarification и unresolved финала раздельны; queue/active/wall не смешаны.

## 11. Неизвестные и блокировки

- Полный live App installation/repository inventory: blocked approval; семь клонов не authoritative total. Не повторять отклонённый доступ без ответа владельца.
- Current board/project mapping всех repo и permissions installations: не проверены; AI-Wrapper binding задан в карточке, не read-back live binding.
- Совместный durable ownership ledger, fencing, preclaim veto, atomic cancel-by-run/park и bridge branch-only API **ещё не реализованы/не найдены как готовый public contract**. Это главные go-live blockers, не косметика.
- HTTP Kanban reachable 401, HTTP run API на live server не подтверждён. Нельзя обещать authenticated HTTP adapter без проверки. Доступность Python source/CLI не подтверждает model route или публикационные права.
- Effective model/provider/auxiliary billing/quota, isolation/egress/resources, safe secret injection и test runner privileges не проверялись и не менялись. Не копировать `.env`, auth stores/ключи в service или worker.
- Usage coverage по всем calls, run→session attribution и hard budget enforcement не испытаны; известна проблема missing→0 JSONL. Observer payloads проверены по docs/code, не runtime capture.
- Установленные Kanban reclaim/block/retry semantics требуют отрицательных тестов, не устных гарантий. Existing observer hooks не admission control. Готового решения «без изменений native core» не доказано.
- Большой feature без meta issue пока не имеет verified bridge mapping; сохранить существующие integration flows, новый вариант согласовать отдельно.

## 12. Официальные источники и выполненные проверки

Официальные страницы прочитаны 2026-10-16 через HTTPS (HTTP 200); extractor не поддержал fetch в текущем backend, применён обычный `urllib`/`curl`, без изменения настройки:

- [Полный индекс возможностей](https://hermes-agent.nousresearch.com/docs/llms.txt).
- [Programmatic Integration](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration): ACP, gateway JSON-RPC и HTTP `/v1/runs`, status/events/stop. Не переносить website-only возможности в установленную версию без code check.
- [Build a Hermes Plugin](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins): native plugins, state и lifecycle hooks; post-commit observers.
- [Observer Hooks](https://hermes-agent.nousresearch.com/docs/developer-guide/observer-hooks): correlation IDs, API/auxiliary/tool events и privacy; сами hooks не durable очередь.
- [Webhooks](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/webhooks): signatures, event/payload filters, delivery; не global ownership protocol.
- [Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban): durable tasks/runs, dependencies, completion contracts, terminate/reclaim. Документируемая атомарная claim не устраняет create-idempotency race в установленном `K:1250`.
- Desktop SDK reference загружен из skill; [официальный SDK](https://hermes-agent.nousresearch.com/docs/developer-guide/desktop-plugin-sdk) приведён как дополнительный reference, отдельный live HTTP fetch этой страницы не выполнялся.

Реально выполнены: чтение перечисленных проектных файлов/skill refs; CLI version/help и exact card show; source tracing path:line; git status/revision; read-only bridge health, Docker mount/clone metadata и сверка трёх live source checksums; discovery реального serve socket и безопасные HTTP GET; авторизационная проверка gh без токена и один заблокированный запрос inventory. **Не выполнены:** model/worker run, dispatch, lifecycle/recovery/stop тесты, создание/изменение карточек/labels/issues/PR, публикация, установка plugin/service, изменение live config, выпуск token, коммит. Проверка самого Markdown и сохранности рабочей области выполняется после записи; её результат — в handoff, а не вымышленный PASS этих E0–E6.
