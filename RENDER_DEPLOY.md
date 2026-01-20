# Деплой бота на Render

## Инструкция по деплою

### 1. Подготовка к деплою

1. Убедитесь, что все файлы закоммичены в Git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Загрузите на GitHub:
   - Создайте новый репозиторий на GitHub
   - Загрузите код:
   ```bash
   git remote add origin https://github.com/yourusername/tower-bot.git
   git push -u origin main
   ```

### 2. Создание сервиса на Render

1. Зайдите на [render.com](https://render.com) и войдите в аккаунт
2. Нажмите "New +" → "Web Service"
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Name**: `tower-bot` (или любое другое имя)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free (или выберите нужный план)

### 3. Переменные окружения

В настройках сервиса добавьте переменные окружения:
- `BOT_TOKEN` = `8093170790:AAHt36R8ScwD6o9Ya-8Wo7DyH8x215HpH-E`
- `PORT` = `10000` (Render автоматически назначает порт, но можно указать)
- `PYTHON_VERSION` = `3.11.0`

Или используйте `render.yaml` для автоматической настройки.

### 4. Установка вебхука

После деплоя получите URL вашего сервиса (например: `https://tower-bot.onrender.com`)

Установите вебхук, открыв в браузере:
```
https://tower-bot.onrender.com/set_webhook?url=https://tower-bot.onrender.com/webhook
```

Или через curl:
```bash
curl "https://tower-bot.onrender.com/set_webhook?url=https://tower-bot.onrender.com/webhook"
```

### 5. Проверка работы

1. Отправьте `/start` боту в Telegram
2. Проверьте логи на Render (вкладка "Logs")
3. Убедитесь, что нет ошибок

### Важные моменты:

- **Render автоматически останавливает бесплатные сервисы** через 15 минут бездействия
- При первом запросе сервис запускается (~30 секунд)
- Для постоянной работы нужен платный план или другой хостинг
- База данных `bot.db` будет сбрасываться при перезапуске (для продакшена лучше использовать PostgreSQL)

### Альтернативы для постоянной работы:

1. **Railway.app** - бесплатный план с постоянной работой
2. **Heroku** - платный (но стабильный)
3. **VPS** - полный контроль, но нужно настраивать самому

### Структура файлов для Render:

```
tower_bot/
├── bot.py              # Основной файл бота с вебхуками
├── database.py         # Работа с БД
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости
├── render.yaml         # Конфигурация Render (опционально)
└── README.md           # Документация
```

### Обновление бота:

1. Внесите изменения в код
2. Закоммитьте и запушьте в GitHub:
   ```bash
   git add .
   git commit -m "Update bot"
   git push
   ```
3. Render автоматически пересоберет и перезапустит сервис
