# Адаптация Tortuga-AI для Hermes — t_95b161ac

## Результат
Файловая часть выполнена: три переносимых проектных скилла версии 0.1.0 и две
справки; исследование → исправление → self-review реально проведены в текущей
агентной сессии на синтетическом обработчике quantity. Карточка не изменялась.
Это не Kanban E2E и не независимое ревью; приёмка владельцем ещё требуется.

## Источники и baseline
- Tortuga-AI commit `6fcde6883a26d94563ffe6a781bec8f7719b0e1d`; прочитаны agent-research,
  agent-implement, agent-review, staff-engineer-review, code-security-auditor,
  frontend-implement, webapp-testing, local-user. SHA-256 каждого — в
  `experiments/t_95b161ac/run-01/provenance.json`; исходники без изменения.
- Рабочая ветка при начале `feat/recovery-lab-t_484bba3b`, HEAD отсутствует.
  Общая unborn-ветка сохранена: переключение затронуло бы другие работы. Коммит
  запрещён, поэтому ограниченный локальный тест идентифицируется хешами файлов,
  а полноценное сравнение методологий из одного Git baseline не заявляется.
- Hermes `v0.21.6+730.g97a9ae8`, Python CLI Hermes 3.14.7. Модель текущей сессии
  `gpt-6-astra`, provider `pool` по runtime context; фактический upstream неизвестен.
- Официальные документы прочитаны через HTTPS: `/docs/llms.txt` и
  https://hermes-agent.nousresearch.com/docs/user-guide/features/skills .
  web_extract оказался недоступен с backend ddgs; чтение выполнено curl.
  Документация описывает SKILL.md и discovery; настройка discovery не выполнялась.

## Что сохранено и изменено
| Оригинал | Адаптация |
|---|---|
| Research: BLUF, reuse/root cause, продуктовые вопросы, quality-before-code, test strategy | Сохранено; scope marker не запускает decomposition |
| Запрет branch creation, т.к. runner создаёт branch | Проверка фактической ветки/HEAD; без предположения о runner; общий checkout не переключать |
| Claude paths, /tmp registration/report, local-user env | Относительные project paths, read_file, отдельные run artifacts; ясная краткость без искажения предупреждений |
| Implement: targeted only; полный suite запускает runner | Implementer обязан запустить полный согласованный suite детерминированной командой |
| Runner commit/push/PR и post_report | Commit/push/PR отключены в local-only scope; отдельный human gate, никакого скрытого publisher |
| Runner fix-resume/retries | Оператор диагностирует; не более одной явно разрешённой повторной попытки пилота; quota/deny/timeout → stop/handoff |
| Review требует PR и запрещает любые тесты | Локальный review допустим; reviewer повторяет ограниченные проверки, сверяет актуальные хеши |
| Staff/security отдельные sub-skills | Содержательные проверки объединены в review reference; без вложенных процессов |
| Frontend tool/container assumptions | Существующие инструменты проверять; нет auto-install или обещания sandbox; UI evidence отдельно |
| Auto attribution/model footer | Явные версии, источники, расходы unknown |

Полные тесты и сохранение evidence принадлежат исполнителю; независимая приёмка —
владельцу. Claim/reclaim/диспетчер остаются отдельно настроенной инфраструктурой;
этот пакет их не реализует. writing-plans/planning-tests/implementing-tasks не нужны.
make-feature и bulletproof не подключались и не сравнивались.

## Реальное испытание
Артефакты: `experiments/t_95b161ac/run-01/`.
1. `research.md`: пять критериев, разрешённые файлы, стратегия, exact commands.
2. `test_quantity.py` написан до исправления. `fixtures/baseline.py` содержит намеренную
   ошибку isinstance(True, int): принимает bool как количество.
3. `red.json`: реальный exit 1, 9 тестов, ровно один сбой `test_reject_bool(value=True)`.
4. `fixtures/fixed.py`: exact-int guard. `green.json` и `review-rerun.json`: exit 0,
   по 9 тестов с одинаковыми ID, без skips/errors.
5. `final-tests.json`: exit 0, 6 проверок структуры/контрактов; внутри реально запускаются
   baseline и два fixed-набора. Syntax проверяется ast; фронтматтер — структурно,
   это не интеграционный тест Hermes skill loader.
6. `implement.md`, `review.md`: фактический handoff и same-agent review. Вердикт APPROVE
   относится только к синтетическому локальному контракту, не к production/профилю.

Все команды имеют 30s subprocess timeout; длительность выполнения записана в JSON.
Никаких автономных повторных workers не запускалось. Повтор fixed-набора — плановый
контроль стабильности, не recovery retry. Изменены мелкие typing diagnostics harness,
после чего suite повторён. Контрактные тесты prose написаны после адаптации, не TDD;
исправление самой quantity-ошибки прошло red→green с неизменными assertions.

## Независимая проверка
Из корня репозитория:
```sh
python -B -m unittest discover -s tests/skills -p 'test_tortuga_skills.py' -v
python -B experiments/t_95b161ac/test_quantity.py --variant baseline
python -B experiments/t_95b161ac/test_quantity.py --variant fixed
sha256sum -c experiments/t_95b161ac/run-01/manifest.sha256
```
Вторая команда ДОЛЖНА вернуть 1 с bool-дефектом; первая/третья/четвёртая — 0.
Тесты только stdlib, без сети/пакетных установок. Bash-скрипты не добавлялись,
поэтому bash -n не применим. Тесты чужих экспериментов не запускались: полный набор
здесь означает весь добавленный контракт, а не все процессы общего репозитория.

## Ограничения и передача
- Не установлены скиллы в профиль, не изменены installed Hermes, сервисы, настройки,
  второй мозг или исходный Tortuga-AI. Commit/push/PR/публикаций нет.
- Это sequential role application текущим агентом, не три независимых агента.
  Скриптовые проверки не объявляются доказательством качества LLM workflow в целом.
- Нет HTTP/UI, dispatcher/recovery/quota/human-gate E2E или security isolation test.
  Этот локальный smoke не означает прохождения всех P01–P12 архитектуры.
- Токены, квота, стоимость, CPU/RAM peaks неизвестны. Измерено только время команд;
  не заявляется нулевой расход модели или сравнение экономичности.
- Дополнительных вмешательств владельца внутри trial не было; запуск и разрешение
  на проектные skills заданы исходным запросом. Текущая работа уже делегирована
  родителем; новых вложенных агентов здесь не создавалось.
- У upstream нет найденного tracked LICENSE/COPYING: не выдумана MIT-лицензия.
  LicenseRef-Upstream-Unverified — маркер неопределённости, не право публикации.
- Аудит остальных карточек и отдельный тикет настройки профиля остаются родителю.
  Карточка t_95b161ac только прочитана; не закрывать без решения родителя/владельца.

Существующие README/architecture/другие эксперименты не переписывались. Навигация
нового пакета: `skills/README.md`; source hashes/provenance и file manifest приложены.
