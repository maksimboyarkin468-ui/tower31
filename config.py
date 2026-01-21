# Конфигурация бота
import os

# Токен бота (берется из переменных окружения или дефолтное значение)
# НЕ ХРАНИТЕ ТОКЕН В РЕПОЗИТОРИИ! Используйте переменные окружения на сервере
BOT_TOKEN = os.getenv('BOT_TOKEN', '8093170790:AAHt36R8ScwD6o9Ya-8Wo7DyH8x215HpH-E')

# ID администратора
ADMIN_ID = 1226518807

# Имя канала для подписки (без @)
CHANNEL_USERNAME = "maksoncikaz"

# Ссылка на поддержку
SUPPORT_LINK = "https://t.me/nomep999"

# Дефолтная реферальная ссылка
DEFAULT_REFERRAL_LINK = "https://t.me/LB_Grid_bot/app?startapp=bXN0PTB4NDkxYjMxMTcmbT1zdG9wa2EmYz1Kc2hldXVlag"

# Пути к изображениям (можно использовать URL или file_id из Telegram)
# Для получения file_id: отправьте фото боту через @userinfobot или другой бот
MAIN_MENU_PHOTO = os.getenv('MAIN_MENU_PHOTO', '')  # URL или file_id фото для главного меню
DEPOSIT_PHOTO = os.getenv('DEPOSIT_PHOTO', '')  # URL или file_id фото для окна депозита
WAITING_PHOTO = os.getenv('WAITING_PHOTO', '')  # URL или file_id фото для ожидания доступа
ACCESS_GRANTED_PHOTO = os.getenv('ACCESS_GRANTED_PHOTO', '')  # URL или file_id фото для доступа к сайту
