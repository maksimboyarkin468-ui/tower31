# С нуля: новый репозиторий на GitHub и деплой на Railway

Пошагово — без лишнего. Делай по порядку.

---

## Часть 1. Новый репозиторий на GitHub

### Шаг 1.1. Создать репозиторий на GitHub

1. Зайди на **https://github.com** и войди в аккаунт.
2. Справа вверху нажми зелёную кнопку **New** (или **+** → **New repository**).
3. Заполни:
   - **Repository name:** например `tower-bot` (латиница, без пробелов).
   - **Description:** по желанию, можно пусто.
   - **Public.**
   - **НЕ ставь** галочки "Add a README", "Add .gitignore", "Choose a license" — репозиторий должен быть **пустой**.
4. Нажми **Create repository**.

После создания GitHub покажет страницу с подсказками. **URL репозитория** будет такой:
`https://github.com/ТВОЙ_ЛОГИН/tower-bot.git`  
(подставь свой логин и имя репо, если назвал по-другому). Этот URL понадобится ниже.

---

## Часть 2. Привязать папку tower_bot к новому репозиторию

У тебя код уже в папке `c:\Users\boiar\tower_bot`. Нужно сказать Git, что теперь мы пушим в **новый** репозиторий.

### Шаг 2.1. Открыть терминал в папке проекта

В Cursor открой терминал (View → Terminal или внизу экрана) и перейди в папку:

```powershell
cd c:\Users\boiar\tower_bot
```

### Шаг 2.2. Убрать старую привязку к GitHub (старый репозиторий)

Введи по очереди (после каждой — Enter):

```powershell
git remote remove origin
```

Так мы отвязываем папку от старого репозитория `toweryuiop`.

### Шаг 2.3. Привязать к новому репозиторию

Подставь **свой логин** и **название нового репозитория** (как создал в шаге 1.1):

```powershell
git remote add origin https://github.com/ТВОЙ_ЛОГИН/tower-bot.git
```

Пример: если логин `maksimboyarkin468-ui` и репо назвал `tower-bot`:

```powershell
git remote add origin https://github.com/maksimboyarkin468-ui/tower-bot.git
```

### Шаг 2.4. Отправить весь код в новый репозиторий

```powershell
git add .
git status
```

Проверь, что в списке есть нужные файлы (bot.py, config.py, database.py и т.д.). Потом:

```powershell
git commit -m "Первый коммит: бот с постбэками 1win и 4 фото"
git push -u origin main
```

Если попросит логин/пароль:
- **Username:** твой логин GitHub.
- **Password:** **токен** (не пароль). Как сделать токен: GitHub → Settings → Developer settings → Personal access tokens → Generate new token (classic), отметить **repo** → скопировать и вставить в пароль.

После успешного `git push` весь код будет в **новом** репозитории на GitHub.

---

## Часть 3. Деплой на Railway

### Шаг 3.1. Создать проект на Railway

1. Зайди на **https://railway.app** и войди (через GitHub удобнее).
2. Нажми **New Project**.
3. Выбери **Deploy from GitHub repo**.
4. Если попросит — разреши Railway доступ к GitHub (выбери аккаунт).
5. В списке репозиториев выбери **новый** репозиторий (тот, что только что создал, например `tower-bot`).
6. Нажми на него. Railway создаст проект и начнёт первый деплой.

### Шаг 3.2. Добавить переменные окружения

1. В проекте Railway открой свой **сервис** (один блок/карточка).
2. Перейди во вкладку **Variables** (или **Settings** → Variables).
3. Нажми **Add Variable** или **New Variable** и добавь по одной:

| Переменная        | Значение                          | Обязательно |
|-------------------|-----------------------------------|-------------|
| `BOT_TOKEN`       | Токен бота от @BotFather          | да          |
| `ADMIN_ID`        | Твой Telegram ID (число)          | да          |
| `WEBHOOK_URL`     | Пока не заполняй — добавим после  | нет (можно потом) |
| `CHANNEL_DISCUSSION_GROUP_ID` | `-1003810391629`        | уже в коде по умолчанию |
| `POSTBACK_USER_ID_REGEX`       | можно не задавать — в коде есть дефолт | нет |

Сохрани переменные. Railway перезапустит деплой.

### Шаг 3.3. Выдать домен (получить URL)

1. В том же сервисе открой вкладку **Settings** (или **Networking**).
2. Найди блок **Networking** / **Public Networking** и нажми **Generate Domain** (или **Add Domain**).
3. Railway выдаст домен вида: `xxx.up.railway.app`. Скопируй его.

Пример: `web-production-049a6.up.railway.app`.

### Шаг 3.4. Установить вебхук

Подставь **свой** домен от Railway в оба места:

Открой в браузере (одной строкой):

```
https://ТВОЙ_ДОМЕН.up.railway.app/set_webhook?url=https://ТВОЙ_ДОМЕН.up.railway.app/webhook
```

Пример:

```
https://web-production-049a6.up.railway.app/set_webhook?url=https://web-production-049a6.up.railway.app/webhook
```

Должен вернуться JSON примерно такой:

```json
{"status":"success","webhook_url":"https://...","webhook_info":{...}}
```

Если видишь `"status":"success"` — вебхук установлен, бот будет получать сообщения из Telegram.

### Шаг 3.5. (По желанию) Записать WEBHOOK_URL в переменные

В Railway → Variables добавь:

- **Key:** `WEBHOOK_URL`
- **Value:** `https://ТВОЙ_ДОМЕН.up.railway.app/webhook`

Так при следующем деплое бот сам подставит этот URL при старте.

---

## Часть 4. Проверка

1. **Health:** открой в браузере  
   `https://ТВОЙ_ДОМЕН.up.railway.app/health`  
   Должно быть: `{"status":"ok"}`.

2. **Бот в Telegram:** напиши боту `/start`. Должен ответить и показать меню.

3. **Логи Railway:** в проекте Railway открой вкладку **Deployments** → выбери последний деплой → **View Logs**. Не должно быть красных ошибок; можно увидеть строку про установку вебхука.

---

## Краткий чеклист

- [ ] Создан **новый** пустой репозиторий на GitHub.
- [ ] В папке `tower_bot`: `git remote remove origin`, потом `git remote add origin https://github.com/ЛОГИН/ИМЯ_РЕПО.git`.
- [ ] Выполнены `git add .`, `git commit -m "..."`, `git push -u origin main`.
- [ ] На Railway создан **New Project** → **Deploy from GitHub repo** → выбран новый репозиторий.
- [ ] В Railway добавлены переменные `BOT_TOKEN`, `ADMIN_ID`.
- [ ] В Railway выдан домен (Generate Domain).
- [ ] В браузере открыт `.../set_webhook?url=.../webhook` — в ответе `"status":"success"`.
- [ ] В Telegram бот отвечает на `/start`.

Если на каком-то шаге что-то пойдёт не так — напиши, на каком именно шаге и что видишь (скрин или текст ошибки).
