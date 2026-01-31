# Конфигурация бота
import os
from pathlib import Path

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

# Путь к папке с изображениями
IMAGES_DIR = Path(__file__).parent / 'images'

def get_photo_path(photo_name):
    """Получает путь к фото из переменной окружения или папки images"""
    # Сначала проверяем переменную окружения
    env_photo = os.getenv(photo_name.upper() + '_PHOTO', '')
    if env_photo:
        return env_photo
    
    # Если нет переменной, ищем файл в папке images
    if IMAGES_DIR.exists():
        # Пробуем разные расширения
        for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
            photo_path = IMAGES_DIR / (photo_name + ext)
            if photo_path.exists():
                return str(photo_path.absolute())
    
    return ''

# Пути к изображениям (автоматически ищет в папке images или берет из переменных окружения)
MAIN_MENU_PHOTO = get_photo_path('main_menu')
DEPOSIT_PHOTO = get_photo_path('deposit')
WAITING_PHOTO = get_photo_path('waiting')
ACCESS_GRANTED_PHOTO = get_photo_path('access_granted')

# Постбэки 1win: группа обсуждения канала (комментарии), куда приходят постбэки
# Форматы: регистрация {sub1}, первый депозит {sub1}|{country}|Firstdep|{amount}, повторный {sub1}|{country}|{amount}
CHANNEL_DISCUSSION_GROUP_ID = os.getenv('CHANNEL_DISCUSSION_GROUP_ID', '-1003810391629')
# Извлечение sub1 (ID пользователя 1win): первый сегмент до |. Регулярка: первая группа = sub1
POSTBACK_USER_ID_REGEX = os.getenv('POSTBACK_USER_ID_REGEX', r'^([^|]+)')
