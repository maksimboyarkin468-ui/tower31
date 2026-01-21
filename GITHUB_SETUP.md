# Инструкция по созданию репозитория на GitHub

## Шаг 1: Создайте репозиторий на GitHub

1. Зайдите на [github.com](https://github.com)
2. Нажмите "+" в правом верхнем углу → "New repository"
3. Заполните:
   - **Repository name**: `tower-bot` (или любое другое имя)
   - **Description**: `Telegram bot for Tower Rush signals`
   - **Visibility**: Public или Private (выберите сами - это НЕ влияет на доступность бота!)
   - **Add .gitignore**: Выберите **Python** (или можно оставить "None" - у нас уже есть свой .gitignore)
   - **Add a license**: Можно выбрать "MIT" или оставить "None"
   - ❌ НЕ ставьте галочку "Initialize with README" (у нас уже есть README.md)
   
   ⚠️ ВАЖНО: Публичность GitHub репозитория НЕ влияет на доступность бота в Telegram!
   - Public репозиторий = код виден всем (но бот работает так же)
   - Private репозиторий = код виден только вам (бот работает так же)
   - Пользователи находят бота в Telegram по имени @your_bot_name, независимо от репозитория!
4. Нажмите "Create repository"

## Шаг 2: Подготовьте файлы локально

### Файлы которые НУЖНО загрузить:

✅ **ОБЯЗАТЕЛЬНЫЕ:**
- `bot.py` - основной файл бота
- `database.py` - работа с базой данных
- `config.py` - конфигурация (НО уберете токен!)
- `requirements.txt` - зависимости
- `README.md` - описание проекта
- `.gitignore` - что не коммитить

✅ **ДЛЯ RENDER:**
- `render.yaml` - конфигурация Render
- `Procfile` - для запуска на Render
- `RENDER_DEPLOY.md` - инструкция по деплою

✅ **ДОПОЛНИТЕЛЬНЫЕ:**
- `DEPLOY.md` - инструкция по деплою
- `TESTING.md` - инструкция по тестированию

### Файлы которые НЕ НУЖНО загружать:

❌ **НЕ ЗАГРУЖАЙТЕ:**
- `bot.db` - база данных (будет создаваться на сервере)
- `__pycache__/` - кэш Python
- `test_bot.py` - тестовые файлы
- `run_test.py` - тестовые файлы
- `START_BOT.bat` - локальные скрипты
- `.env` - файлы с переменными окружения

## Шаг 3: Удалите токен из config.py

**ВАЖНО!** Перед загрузкой на GitHub:

1. Откройте `config.py`
2. Удалите или замените токен:
   ```python
   # ВМЕСТО:
   BOT_TOKEN = "8093170790:AAHt36R8ScwD6o9Ya-8Wo7DyH8x215HpH-E"
   
   # СДЕЛАЙТЕ:
   BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TOKEN_HERE')
   ```
3. Добавьте в начало файла:
   ```python
   import os
   ```

## Шаг 4: Загрузите файлы через Git

### Если Git еще не установлен:

1. Скачайте Git: https://git-scm.com/download/win
2. Установите его

### Команды для загрузки:

Откройте PowerShell или командную строку в папке проекта:

```bash
# 1. Инициализируйте Git репозиторий
git init

# 2. Добавьте все файлы (кроме тех, что в .gitignore)
git add .

# 3. Сделайте первый коммит
git commit -m "Initial commit: Tower Bot"

# 4. Добавьте удаленный репозиторий (замените YOUR_USERNAME на ваш GitHub логин)
git remote add origin https://github.com/YOUR_USERNAME/tower-bot.git

# 5. Загрузите файлы на GitHub
git branch -M main
git push -u origin main
```

## Шаг 5: Добавьте переменные окружения на Render

После деплоя на Render добавьте переменную окружения:
- **Key**: `BOT_TOKEN`
- **Value**: `8093170790:AAHt36R8ScwD6o9Ya-8Wo7DyH8x215HpH-E`

## Безопасность:

✅ **ПРАВИЛЬНО:**
- Токен хранится в переменных окружения на Render
- `.gitignore` исключает `.env` и `.db` файлы
- Репозиторий может быть публичным

❌ **НЕПРАВИЛЬНО:**
- Хранить токен прямо в `config.py` в репозитории
- Коммитить `.db` файлы
- Публиковать секретные данные
