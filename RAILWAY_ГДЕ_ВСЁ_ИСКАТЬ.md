# Railway: где искать Volume и домен (если «ничего нет»)

Кратко — куда заходить и что нажимать в текущем интерфейсе Railway.

---

## Volume (постоянный диск для базы)

**Отдельной вкладки «Volumes» нет.** Volume создаётся так:

### Способ 1 — палитра команд (надёжно)

1. Открой **страницу проекта** (где видны карточки сервисов).
2. Нажми **Ctrl+K** (Windows) или **Cmd+K** (Mac).
3. В поле ввода напиши **Volume** или **Create Volume**.
4. Выбери пункт вроде **Create Volume** / **Add Volume**.
5. Выбери сервис бота → укажи **Mount Path**: `/data` → создай.

### Способ 2 — правый клик по фону

1. На странице проекта нажми **правой кнопкой по пустому месту** (по фону, не по карточке сервиса).
2. В меню выбери **Create Volume** / **Add Volume**.
3. Дальше — выбрать сервис и Mount Path `/data`.

После создания Volume добавь в **Variables** переменную:
- **DATABASE_PATH** = `/data/bot.db`

Официальная инструкция: https://docs.railway.com/guides/volumes

---

## Домен (публичный URL для вебхука)

Домен настраивается в **настройках сервиса**:

1. Зайди в **проект** → кликни по **карточке сервиса бота** (откроется сервис).
2. Открой вкладку **Settings** (Настройки).
3. Прокрути до блока **Networking** / **Public Networking** / **Domains**.
4. Там должна быть кнопка **Generate Domain** или **Add Domain** — нажми её.
5. Если просят порт — укажи тот, на котором слушает бот (часто **8080** или **5000**).
6. Railway покажет домен вида `xxx.up.railway.app`. Скопируй его.

В **Variables** добавь:
- **WEBHOOK_URL** = `https://твой-домен.up.railway.app/webhook`

### Если кнопки Generate Domain нет

- Зайди в **Settings** того же сервиса и проверь блок **TCP Proxy**. Если он **включён** — отключи или удали. После этого часто появляется **Generate Domain**.
- Домен может называться **Public Networking** → **Generate Domain** или просто **Domains** → **Add**.

Официально: **Settings → Networking → Public Networking → Generate Domain**.

---

## Чеклист «что где»

| Что нужно | Где искать |
|-----------|------------|
| **Volume** | **Ctrl+K** → ввести «Volume» **или** правый клик по **фону** проекта → Create Volume |
| **Домен** | Сервис → **Settings** → вниз до **Networking** / **Public Networking** → **Generate Domain** |
| **Variables** | Сервис → вкладка **Variables** (рядом с Deployments, Settings) |

Если интерфейс на railway.com выглядит иначе — сверься с актуальными гайдами:
- Volumes: https://docs.railway.com/guides/volumes  
- Public domains: https://docs.railway.com/reference/public-domains
