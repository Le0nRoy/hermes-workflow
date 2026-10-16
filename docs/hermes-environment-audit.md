# Среда Hermes и фактические границы доступа

Дата проверки: 2026-10-15, 02:23–02:24 +04:00. Карточка: `t_dc67ac7c`.
Статус: выполнен ограниченный read-only аудит, не сертификация безопасности.

## 1. Область и разрешение

Основание запуска — прямой запрос `work kanban task t_dc67ac7c`. Он относится только к этой карточке, не утверждает архитектуру A1 и не разрешает внедрение или разблокировку остальных карточек. Прочитаны AGENTS.md, README.md, индекс базы знаний и заметки об агентных процессах/ресурсах; личные сведения сюда не перенесены. Старый `environment-audit.md` использован для навигации, факты ниже проверены заново.

Read-only относится к целевой среде: настройки, права, сервисы, контейнеры, другие профили и репозитории не изменялись. Записи этой работы — данный отчёт и lifecycle собственной карточки. CLI и средства просмотра могут создавать обычные runtime/cache данные. Не выполнялись sudo, эксплуатация Docker-доступа, чтение секретов, логины, inference-пробы, установка, deploy, commit, push, перезапуск или остановка сервисов.

В отчёте `$HOME` заменяет персональный домашний путь. Адреса LAN/Tailscale, публичное имя Funnel, аккаунты, содержимое env/auth и команды с credential-аргументами не сохраняются. Имена технических сервисов и репозиториев оставлены для воспроизводимости.

## 2. Ключевой вывод

Текущий Hermes работает на хосте primary-host как обычный пользователь UID 1000 с terminal backend `local`. Workspace и профиль не ограничивают его доступ директорией задачи. Подтверждены доступ к метаданным других проектов, право записи в каталог Tortuga-AI, читаемость собственного auth store по проверке прав и доступ к rootful Docker daemon через сокет. Это не изолированный контур для недоверенного кода или клиентских секретов.

Особенно существенен Docker: пользователь входит в группу `docker`, сокет доступен для записи, `docker version/info/ps` действительно работают, daemon системного сервиса работает с UID 0. Такой доступ даёт потенциально root-equivalent полномочия через API. Повышение прав не демонстрировалось; наличие application approvals не превращает эти полномочия в OS sandbox.

Подтверждены и реальные ограничения: `/root` недоступен текущему пользователю для чтения/обхода по `test`; чтение namespace-ссылок PID 1 и firewall ruleset получило Permission denied. Секретные файлы Hermes защищены от обычных других UID правами 0600 и родителем 0700, но не от агента с тем же UID.

## 3. Версии, рабочие области, профили

| Объект | Проверенный результат |
|---|---|
| Хост | `uname -nsrmo`: primary-host, Linux 7.2.9-arch1-1, x86_64 GNU/Linux |
| Пользователь | UID/GID 1000; дополнительные группы sddm, docker, video, input, wheel |
| Hermes | v0.21.6+730.g97a9ae8 (2026.9.24), stable, git-install |
| Установка | `$HOME/.hermes/hermes-agent`, HEAD `97a9ae8ee55d31bebce49f1fb6b5ef775323976a`; `git status --short` пуст |
| Runtime CLI | Python 3.14.7, OpenAI SDK 2.24.0 |
| Профили | `hermes profile list`: только default, модель gpt-6-astra, gateway running; каталог `$HOME/.hermes/profiles` отсутствует |
| Hermes home | `$HOME/.hermes` |
| Workspace | `${HERMES_WORKFLOW_ROOT}`, kind `dir` по карточке |
| Git workspace | `chore/bootstrap`, unborn HEAD; `git rev-parse HEAD` завершился ошибкой отсутствия revision; worktree list показывает единственную текущую директорию с нулевым HEAD |
| Исходное состояние | `.gitignore`, AGENTS.md, README.md, docs/, experiments/ — untracked; чужие файлы не изменены |
| Соседний проект | `${TORTUGA_AI_ROOT}`, HEAD `1c65e5a555464a006b51feb44132322e5c2d7dc8`, ветка `agent/feature-663` |
| Его worktree metadata | `worktrees/support-codex`, HEAD `ece68878911f29a89c67556c8a1b4b3fe0517cc1`, пометка `prunable: gitdir file points to non-existent location`; repair/prune не выполнялся |
| Файловая система проекта | `/Data`, ext4, `rw,relatime` |

Существующая немагистральная ветка сохранена: переключение общей директории при параллельной работе небезопасно, первый коммит не разрешён этой карточкой. Worktree — отдельное рабочее дерево Git, а не отдельные OS-права. Отсутствие других профилей в штатном списке не доказывает отсутствие любых альтернативных установок на всём диске.

## 4. Запуск и сервисы

Штатные свойства user systemd проверены без чтения Environment и credential-файлов.

| Сервис | Факты |
|---|---|
| `hermes-gateway.service` | enabled, active/running; MainPID 1392455; WorkingDirectory `$HOME/.hermes`; ExecStart — установленный `hermes gateway run`; Restart=always, NRestarts=3 |
| `cliproxy.service` | enabled, active/running; MainPID 3618450; WorkingDirectory `$HOME/.hermes/cliproxy`; запуск `cli-proxy-api --config …/config.yaml --local-model` |
| `docker.service` | active, MainPID 25979; `ps` подтверждает UID 0 у этого dockerd |
| Worker карточки | PID 1850683, PPID 1392455, UID 1000, comm hermes; родитель совпадает с MainPID gateway |
| Другие Hermes-процессы | PID 1850667 также дочерний gateway; PID 1106354 имеет PPID 1. Назначение последнего и единственность dispatcher не установлены |

Это уточняет старый аудит: именно текущий worker связан по PPID с gateway. Не следует переносить этот вывод на все прежние workers. Cgroup gateway: `/user.slice/user-1000.slice/user@1000.service/app.slice/hermes-gateway.service`; принадлежность worker к нему отдельно не доказана. `Restart=always` не является тестом восстановления задач.

Systemd hardening:

- Gateway: NoNewPrivileges=no, PrivateTmp=no, PrivateNetwork=no, PrivateUsers=no, ProtectHome=no, ProtectSystem=no.
- Proxy: NoNewPrivileges=yes и PrivateTmp=yes, но PrivateNetwork=no, PrivateUsers=no, ProtectHome=no, ProtectSystem=no.
- CapabilityBoundingSet сервисов широкий; это верхняя граница, не доказательство реально выданных capabilities. У worker `getpcaps` показывает только `cap_wake_alarm=i`, без effective/permitted capabilities в выводе.

`docker ps` подтвердил работающий соседний стек: agent-bridge, runners/DinD, docker-proxy, homepage/API, deploy-sidecar, telegram-bot, LiteLLM/БД, Prometheus/Grafana/exporters и Minecraft. Это общий живой хост, не пустая лаборатория. Есть здоровые контейнеры, контейнеры без отображённого health-status и `minecraft-server-auth-sidecar-1` с unhealthy; причины не исследовались, исправления вне scope. Контейнеры Tortuga не означают, что Hermes автоматически работает внутри их sandbox. Config/mount/env контейнеров не читались.

## 5. Матрица границ доступа

### Файлы и persistence

Метод: `stat`, `getfacl` целевых путей и цепочек родителей, `test -r/-w/-x`; содержимое auth-файлов не открывалось.

- `$HOME/.hermes`: 0700; `.env` и `auth.json`: 0600, принадлежат UID агента. В проверенных ACL только стандартные owner/group/other, без дополнительных grants. Родители `/home` и `$HOME` — 0755. Защита от обычных других пользователей есть; `test -r auth.json` для текущего UID успешен. Не доказаны наличие действующих токенов, их тип, шифрование или срок действия.
- `$HOME/.ssh`: 0700; ключи не перечислялись и не читались, SSH-agent/remote login не проверялись.
- Каталог workspace и цепочка `${PROJECTS_ROOT}/hermes`: владелец текущий UID, 0755, без расширенных ACL в просмотренных путях. Каталог соседнего Tortuga-AI и его цепочка также доступны; `test -w` на Tortuga-AI успешен. Это подтверждает право на каталог, но не утверждает writable для каждого вложенного файла.
- User systemd directory — 0755, `hermes-gateway.service` — 0644, владелец текущий UID; ACL родителей проверены. Plugins directory — 0755, skills — 0700, также текущего UID. Следовательно, эти persistence-пути не защищены от same-UID записи. Запись не пробовалась.
- `/root`: root:root 0750; текущий UID не прошёл `test -r/-x`. Это локальная DAC-граница, не общая гарантия с учётом Docker authority.

Полного сканирования домашней директории, клиентских файлов, browser stores, SSH keys, backups или файловой системы не было. Не утверждается, что все секреты найдены либо защищены.

### Процессы и namespace

- Видны PID/PPID/UID/comm gateway, workers и root dockerd. Полные argv всех процессов и `/proc/*/environ` не собирались.
- `kernel.yama.ptrace_scope=1`: присутствует ограничение ptrace; это не межпрофильная изоляция. Чтение чужой памяти, ptrace и отправка сигналов не выполнялись.
- `lsns -p 1850683` показал namespace IDs worker: mnt 4026531832, net 4026531833, pid 4026531836, user 4026531837, также time/cgroup/uts/ipc. Прямое сравнение с PID 1 не завершено: `readlink -v /proc/1/ns/*` получило Permission denied. Нельзя выдавать частичный вывод за доказанное совпадение namespace с PID 1.
- `/proc` смонтирован `rw,nosuid,nodev,noexec,relatime`. Сведения о процессах доступны, но это не доказательство доступа ко всем их данным или способности управления всеми процессами.
- Группы input/video/sddm расширяют потенциальную поверхность устройств/GUI; права конкретных устройств и возможность захвата экрана/ввода не проверялись. Захват не выполнялся.

### Docker

- `/run/docker.sock`: root:docker 0660; ACL стандартные; `/run` 0755. Текущий UID в docker, `test -w` успешен.
- CLI context `default`, endpoint `unix:///var/run/docker.sock`; DOCKER_HOST/DOCKER_CONTEXT не выведены как заданные значения.
- Docker Client/Server 29.9.0; `info` сообщает seccomp builtin и cgroupns, не сообщает rootless. Вместе с UID 0 системного daemon это подтверждает rootful путь.
- `version/info/ps` работают без sudo. Отсутствие API-ограничений на write не проверялось мутациями; стандартный прямой rootful socket следует считать root-equivalent риском. Контейнеры, host mounts и privileged probes не создавались.

### Сеть

- Proxy слушает `127.0.0.1:8317`; GET `/v1/models` без ключа вернул HTTP 401. Это проверка одного endpoint, не всего API и не upstream credentials.
- `ss -lntp` также показал wildcard bindings соседних сервисов, включая 22, 80, 3000, 4000, 8080, 8765–8766, 9095, 25565, 25575; внешняя достижимость каждого не проверялась.
- `tailscale funnel status` сообщил включённый публичный Funnel на HTTPS :8443, путь `/` проксируется в `http://127.0.0.1:8765`. Это подтверждённая конфигурация внешней публикации agent-bridge, а не доказательство доступности с независимого внешнего клиента или отсутствия auth. Публичное имя намеренно опущено. На :8317 этот вывод Funnel не указывает.
- Публичный HTTPS GET официального индекса документации через curl успешен: исходящая сеть доступна как минимум к этому адресу. Default-deny egress/allowlist этим не доказаны.
- `nft list ruleset` завершился Operation not permitted. Firewall, sshd policy, NAT и другие пути публикации остаются неизвестными; sudo/Docker для обхода отказа не использовались.

### Прикладные защиты

`hermes config get` подтвердил terminal.backend=local, approvals.mode=smart, approvals.single_query_mode=deny, security.redact_secrets=true, auth.adopt_external_logins=true. Последнее означает настройку допуска импорта, не факт импорта credentials.

Один пакет команд с `python -c` был целиком заблокирован approval policy до исполнения. Политика не ослаблялась; необходимые metadata-проверки выполнены обычными read-only CLI. Это реально наблюдавшийся защитный отказ, но не доказательство полноты фильтра команд и не OS isolation. Redaction — защита вывода, не запрет чтения файлов агентом.

## 6. Безопасные методы повторения

Команды исполнялись из workspace. Для воспроизведения подставлять текущий PID worker из собственной карточки, не считать перечисленные PID постоянными.

```sh
date --iso-8601=seconds
uname -nsrmo
id
hermes --version
hermes profile list
hermes config get terminal.backend
hermes config get approvals.mode
hermes config get approvals.single_query_mode
hermes config get security.redact_secrets
hermes config get auth.adopt_external_logins
git status --short
git branch --show-current
git worktree list --porcelain
systemctl --user show hermes-gateway.service cliproxy.service \
  -p Id -p MainPID -p ActiveState -p SubState -p WorkingDirectory \
  -p NoNewPrivileges -p PrivateTmp -p PrivateNetwork -p PrivateUsers \
  -p ProtectHome -p ProtectSystem
ss -lntp
stat -c '%a %U %G %F %n' /run/docker.sock
getfacl -p /run /run/docker.sock
docker context show
docker context inspect --format '{{.Endpoints.docker.Host}}'
docker version --format 'Client: {{.Client.Version}} Server: {{.Server.Version}}'
docker info --format '{{json .SecurityOptions}}'
ps -C dockerd -o pid,ppid,uid,comm
sysctl kernel.yama.ptrace_scope
curl -sS --max-time 5 -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8317/v1/models
```

Дополнительно использованы точечные `getfacl/stat/test` перечисленных путей, `ps`, `lsns`, `readlink -v`, `findmnt`, `tailscale funnel status`, `nft list ruleset`. Сетевые адреса и имена из live output не переносить в публичный отчёт без необходимости. ExecStart безопасен только после проверки отсутствия секретов в launch arguments; Environment и полный config dump не нужны.

## 7. Детерминированные проверки будущей архитектуры — не выполнены

Предлагаемые критерии не являются уже согласованной архитектурой. Сейчас никаких пользователей, namespace, контейнеров или fixtures не создаётся. Следующий автор может повторять metadata-проверки без изменения среды; интеграционные тесты потребуют отдельно разрешённой лаборатории.

| Проверка | Предусловие и read-only метод | Ожидаемый результат / pass |
|---|---|---|
| Граница файлов | Утверждены разрешённые roots и UID worker; из реального worker проверить `id`, stat/ACL цепочек, test доступа к заранее подготовленным несекретным canary | Workspace доступен, соседний проект и canary вне scope недоступны; совпадает с матрицей требований |
| Credentials | Заранее подготовлены несекретные canary в credential mount и утверждён способ injection | Worker не может читать host credential store/canary; proxy выдаёт только целевой доступ. Реальные секреты не читать |
| Docker authority | Из worker проверить socket existence/access, context и разрешённый read-only API | Нет прямого host rootful socket и обходного Docker API; allowlisted proxy проверяется по конфигурации. Отсутствие CLI само по себе не pass |
| Process isolation | Есть согласованный reference PID и доступ к namespace metadata | PID/user/mount namespaces соответствуют проекту; host process metadata недоступна там, где это требуется; запрет не выводится лишь из названия профиля |
| Network | Утверждён egress allowlist и безопасные контрольные адреса без auth | Разрешённый GET проходит, запрещённый GET блокируется. Для deny пробы нужен заранее согласованный endpoint, не произвольный скан |
| Exposure | Сопоставить ss, Funnel/Serve, reverse-proxy routes и доступные firewall rules | Все опубликованные endpoints входят в утверждённый список; недоступный ruleset означает unknown, не pass |
| Launch hardening | Проверить live unit properties и реальный PID worker | Утверждённые NoNewPrivileges/ProtectHome/ProtectSystem и namespace меры фактически действуют; отдельный proxy unit не засчитывается за worker |
| Worktree reproducibility | После отдельно разрешённого baseline commit — git HEAD/status/worktree list | Не unborn, уникальные валидные worktrees, нет prunable metadata; это критерий воспроизводимости, не security isolation |
| Human start gate | По Kanban events сопоставить запуск каждой карточки с явным разрешением её scope | Auto-decomposition не заменяет согласие владельца; архитектура не считается утверждённой по успешному аудиту |

Recovery после reboot/restart, quota exhaustion, restore резервной копии, отправка сигналов, запись вне workspace и создание контейнеров не могут быть полноценно доказаны только metadata-аудитом. Их следует испытывать отдельно, не на живых сервисах без разрешения.

## 8. Ограничения и передача

- Снимок меняющейся среды, не атомарная инвентаризация; версии на диске не гарантируют версию давно запущенного процесса.
- Клиент Desktop и местоположение model inference не исследованы; backend host не доказывает ни местоположение клиента, ни локальный inference.
- Не проверены MAC/LSM policy полностью, sudo rules, все devices, container mounts/security config, authorization всех API, SSH policy, backups/restore, биллинг и квоты. Имена Backup не считаются свидетельством резервного копирования.
- Проверка `/proc/1/ns/*` и nft ограничена правами; полномочия не повышались. Секреты не запрашивались.
- `web_extract` недоступен с текущим search-only DDGS backend; официальный индекс получен curl, настройки backend не менялись.
- Использованы навыки `hermes-agent` 3.2.0 (security-privacy reference) и `local-privacy-audit` 0.2.0. Официальная карта: https://hermes-agent.nousresearch.com/docs/llms.txt (получена в этой проверке). В ней разделы security, profiles, docker и egress/network-isolation описывают доступные механизмы, но их наличие в документации не означает внедрения здесь.
- Затраты текущей модельной сессии и остаток подписок не измерены; новых платных услуг и дополнительных тестовых inference-запросов не было.

Результат передаётся существующим `t_2fab5f0a` / `t_93841548` как фактический вход для архитектуры. Ни эта карточка, ни отчёт не утверждают решения A1, не разрешают устранение найденных рисков и не запускают внедрение. Исправления живой среды требуют отдельного решения владельца.
