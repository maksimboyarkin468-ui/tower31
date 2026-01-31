import os
import re
import logging
import time
import threading
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes
from telegram.ext import filters
import asyncio
from database import Database
from config import (
    BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, SUPPORT_LINK, DEFAULT_REFERRAL_LINK,
    MAIN_MENU_PHOTO, DEPOSIT_PHOTO, WAITING_PHOTO, ACCESS_GRANTED_PHOTO,
    CHANNEL_DISCUSSION_GROUP_ID, POSTBACK_USER_ID_REGEX
)

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database()

# Таймаут ожидания ввода ID 1win после «Готово» (секунды)
AWAITING_1WIN_TIMEOUT = 15 * 60  # 15 минут

# Общий event loop для бота (работает в фоновом потоке при режиме webhook)
_bot_loop = None

# Создаём приложение бота
bot_application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Добавляем пользователя в БД
    db.add_user(user_id, update.effective_user.username)
    
    # Главное меню
    keyboard = [
        [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
        [InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)],
        [InlineKeyboardButton("⚙️ Панель администратора", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🏠 Добро пожаловать в главное меню!

Вы находитесь в сигнальном боте TOWER BOT AI 🎯

📊 Функционал бота:
• Получение точных сигналов для игры Tower Rush
• Анализ с помощью искусственного интеллекта
• Прогнозирование результатов с высокой вероятностью
• Удобный интерфейс и быстрый доступ к сигналам

Выберите действие из меню ниже 👇"""
    
    # Отправляем фото если указано, иначе просто текст
    if MAIN_MENU_PHOTO:
        await update.message.reply_photo(
            photo=MAIN_MENU_PHOTO,
            caption=welcome_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "get_signal":
        await handle_get_signal(query, context)
    elif data == "admin_panel":
        await handle_admin_panel(query, context)
    elif data == "check_subscription":
        await handle_check_subscription(query, context)
    elif data == "back_to_menu":
        await handle_back_to_menu(query, context)
    elif data == "deposit":
        await handle_deposit(query, context)
    elif data == "deposit_ready":
        await handle_deposit_ready(query, context)
    elif data == "admin_users":
        await handle_admin_users(query, context)
    elif data == "admin_give_access":
        await handle_admin_give_access(query, context)
    elif data == "admin_stats":
        await handle_admin_stats(query, context)
    elif data == "admin_update_referral":
        await handle_admin_update_referral(query, context)
    elif data.startswith("admin_confirm_"):
        target_user_id = int(data.split("_")[-1])
        await handle_admin_confirm_deposit(query, context, target_user_id)


async def handle_get_signal(query, context):
    """Обработчик кнопки 'Получить сигнал'"""
    user_id = query.from_user.id
    
    # Проверяем подписку
    is_subscribed = await check_channel_subscription(context.bot, user_id)
    
    if not is_subscribed:
        # Просим подписаться
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """📢 Для получения сигналов необходимо подписаться на наш канал!

Нажмите кнопку ниже, чтобы перейти к каналу и подписаться."""
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    else:
        # Проверяем доступ
        has_access = db.user_has_access(user_id)
        
        if not has_access:
            # Просим пополнить депозит
            await show_deposit_message(query, context)
        else:
            # Пользователь имеет доступ - показываем сигнал с ссылкой на игру
            web_app_url = "https://tower-b0t-web.vercel.app/"
            keyboard = [
                [InlineKeyboardButton("🎮 Играть сейчас", url=web_app_url)],
                [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = """🎯 ВАШ СИГНАЛ ГОТОВ!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 Для получения сигнала и начала игры нажмите кнопку "Играть сейчас" ниже.

🤖 AI-бот автоматически сгенерирует для вас точный прогноз с вероятностью успеха!

🍀 Удачи в игре!"""
            
            await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_check_subscription(query, context):
    """Проверка подписки на канал"""
    user_id = query.from_user.id
    is_subscribed = await check_channel_subscription(context.bot, user_id)
    
    if is_subscribed:
        # Показываем окно депозита
        await show_deposit_message(query, context)
    else:
        # Снова просим подписаться
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """❌ Вы еще не подписаны на канал!

Пожалуйста, подпишитесь на канал и нажмите кнопку "Я подписался"."""
        
        await query.edit_message_text(text, reply_markup=reply_markup)


async def show_deposit_message(query, context):
    """Показывает окно с просьбой пополнить депозит"""
    referral_link = db.get_referral_link()
    
    keyboard = [
        [InlineKeyboardButton("💳 Пополнить", url=referral_link)],
        [InlineKeyboardButton("✅ Готово", callback_data="deposit_ready")],
        [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """💎 Пополнение депозита

Для получения доступа к сигналам необходимо пополнить депозит в игре.

После пополнения депозита, администратор подтвердит ваш доступ в течение нескольких минут.

💰 Нажмите кнопку "Пополнить" для перехода к пополнению.

После пополнения нажмите кнопку "Готово" 👇"""
    
    # Отправляем фото если указано
    if DEPOSIT_PHOTO:
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=DEPOSIT_PHOTO, caption=text),
                reply_markup=reply_markup
            )
        except Exception as e:
            # Если не получилось изменить медиа, отправляем новое сообщение
            logger.error(f"Ошибка отправки фото депозита: {e}")
            await query.message.reply_photo(
                photo=DEPOSIT_PHOTO,
                caption=text,
                reply_markup=reply_markup
            )
            await query.message.delete()
    else:
        await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_deposit(query, context):
    """Обработчик кнопки пополнения"""
    await show_deposit_message(query, context)


async def handle_deposit_ready(query, context):
    """Обработчик кнопки 'Готово' после пополнения"""
    user_id = query.from_user.id
    
    # Проверяем, есть ли уже доступ
    has_access = db.user_has_access(user_id)
    
    if has_access:
        # Если доступ уже есть, показываем окно с доступом
        await show_access_granted_message(query, context)
    else:
        # Ставим пользователя в режим «ждём ID 1win»
        db.set_awaiting_1win_id(user_id)
        
        keyboard = [
            [InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)],
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """⏳ Проверка депозита (1win)

✅ Ваша заявка принята!

📌 Напишите в этот чат ваш ID на сайте 1win (число или логин) — так мы сверим пополнение с постбэками и откроем доступ.

⏰ ID можно посмотреть в личном кабинете 1win или в письмах от сайта.

🔔 После совпадения с постбэком доступ откроется автоматически. Если постбэк ещё не пришёл — попробуйте через пару минут или напишите в поддержку."""
        
        # Отправляем фото если указано
        if WAITING_PHOTO:
            try:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=WAITING_PHOTO, caption=text),
                    reply_markup=reply_markup
                )
            except Exception as e:
                # Если не получилось изменить медиа, отправляем новое сообщение
                logger.error(f"Ошибка отправки фото ожидания: {e}")
                await query.message.reply_photo(
                    photo=WAITING_PHOTO,
                    caption=text,
                    reply_markup=reply_markup
                )
                await query.message.delete()
        else:
            await query.edit_message_text(text, reply_markup=reply_markup)


async def show_access_granted_message(query, context):
    """Показывает сообщение о предоставленном доступе"""
    web_app_url = "https://tower-b0t-web.vercel.app/"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Перейти к игре", url=web_app_url)],
        [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """✅ Вам открыт доступ к сигнальному боту TOWER BOT AI!

🎉 Поздравляем! Ваш депозит подтвержден администратором.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Теперь вы можете использовать весь функционал нашего бота и получать точные прогнозы с помощью искусственного интеллекта!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ЧТО ВАМ ДОСТУПНО:

• Получать точные сигналы для игры Tower Rush
• Использовать все возможности бота
• Получать прогнозы с высокой вероятностью успеха
• Доступ к веб-приложению для удобной игры
• Круглосуточная поддержка через бота
• Регулярные обновления и улучшения функционала

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 КАК ЭТО РАБОТАЕТ:

Наш бот основан на передовых технологиях искусственного интеллекта и анализирует множество параметров для выдачи наиболее точных сигналов. Каждый прогноз содержит информацию о количестве башен и вероятность успеха в процентах.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Ссылка на этого бота в Web-App:
https://tower-b0t-web.vercel.app/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 СОВЕТЫ:

• Используйте сигналы регулярно для лучших результатов
• Обращайте внимание на процент вероятности успеха
• При возникновении вопросов обращайтесь в поддержку

Используйте кнопки ниже для начала работы! 🚀

Желаем удачной игры и больших выигрышей! 🍀✨"""
    
    # Отправляем фото если указано
    if ACCESS_GRANTED_PHOTO:
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=ACCESS_GRANTED_PHOTO, caption=text),
                reply_markup=reply_markup
            )
        except Exception as e:
            # Если не получилось изменить медиа, отправляем новое сообщение
            logger.error(f"Ошибка отправки фото доступа: {e}")
            await query.message.reply_photo(
                photo=ACCESS_GRANTED_PHOTO,
                caption=text,
                reply_markup=reply_markup
            )
            await query.message.delete()
    else:
        await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_back_to_menu(query, context):
    """Возврат в главное меню"""
    keyboard = [
        [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
        [InlineKeyboardButton("💬 Поддержка", url=SUPPORT_LINK)],
        [InlineKeyboardButton("⚙️ Панель администратора", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """🏠 Добро пожаловать в главное меню!

Вы находитесь в сигнальном боте TOWER BOT AI 🎯

📊 Функционал бота:
• Получение точных сигналов для игры Tower Rush
• Анализ с помощью искусственного интеллекта
• Прогнозирование результатов с высокой вероятностью
• Удобный интерфейс и быстрый доступ к сигналам

Выберите действие из меню ниже 👇"""
    
    # Отправляем фото если указано
    if MAIN_MENU_PHOTO:
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=MAIN_MENU_PHOTO, caption=welcome_text),
                reply_markup=reply_markup
            )
        except Exception as e:
            # Если не получилось изменить медиа, отправляем новое сообщение
            logger.error(f"Ошибка отправки фото главного меню: {e}")
            await query.message.reply_photo(
                photo=MAIN_MENU_PHOTO,
                caption=welcome_text,
                reply_markup=reply_markup
            )
            await query.message.delete()
    else:
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)


async def handle_admin_panel(query, context):
    """Панель администратора"""
    user_id = int(query.from_user.id)
    
    if user_id != ADMIN_ID:
        await query.answer("❌ У вас нет доступа к панели администратора!", show_alert=True)
        return
    
    keyboard = [
        [InlineKeyboardButton("👥 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton("✅ Выдать доступ", callback_data="admin_give_access")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔗 Обновить реферальную ссылку", callback_data="admin_update_referral")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """⚙️ Панель администратора

Выберите действие:

👥 Список пользователей - просмотр всех пользователей
✅ Выдать доступ - подтвердить депозит пользователя
📊 Статистика - общая статистика бота
🔗 Обновить реферальную ссылку - изменить ссылку казино"""
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_admin_users(query, context):
    """Список пользователей для админа"""
    users = db.get_all_users()
    
    if not users:
        text = "👥 Пользователей пока нет."
    else:
        text = "👥 Список пользователей:\n\n"
        for user in users[:20]:  # Показываем первые 20
            user_id, username, has_access = user
            status = "✅ Доступ есть" if has_access else "❌ Нет доступа"
            username_text = f"@{username}" if username else f"ID: {user_id}"
            text += f"{username_text} ({user_id})\n{status}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Панель администратора", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_admin_give_access(query, context):
    """Инструкция по выдаче доступа"""
    text = """✅ Выдача доступа

Для выдачи доступа пользователю используйте команду:
/add <user_id> <уровень_доступа>

Пример:
/add 123456789 1

Где:
- 123456789 - ID пользователя
- 1 - уровень доступа (1 - базовый доступ)"""
    
    keyboard = [[InlineKeyboardButton("🔙 Панель администратора", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_admin_stats(query, context):
    """Статистика бота"""
    stats = db.get_stats()
    
    text = f"""📊 Статистика бота

👥 Всего пользователей: {stats['total_users']}
✅ Пользователей с доступом: {stats['users_with_access']}
📈 Новых за сегодня: {stats['new_today']}"""
    
    keyboard = [[InlineKeyboardButton("🔙 Панель администратора", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_admin_update_referral(query, context):
    """Обновление реферальной ссылки"""
    current_link = db.get_referral_link()
    
    text = f"""🔗 Обновление реферальной ссылки

Текущая ссылка:
{current_link}

Для обновления ссылки используйте команду:
/setref <новая_ссылка>

Пример:
/setref https://t.me/LB_Grid_bot/app?startapp=NEW_LINK"""
    
    keyboard = [[InlineKeyboardButton("🔙 Панель администратора", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)


async def handle_admin_confirm_deposit(query, context, target_user_id):
    """Подтверждение депозита (заглушка)"""
    pass


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /add для админа"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("❌ Использование: /add <user_id> <уровень_доступа>")
        return
    
    try:
        target_user_id = int(context.args[0])
        access_level = int(context.args[1])
        
        db.give_access(target_user_id, access_level)
        await update.message.reply_text(f"✅ Доступ выдан пользователю {target_user_id} (уровень {access_level})")
        
        # Уведомляем пользователя с красивым сообщением
        try:
            web_app_url = "https://tower-b0t-web.vercel.app/"
            keyboard = [
                [InlineKeyboardButton("🎮 Перейти к игре", url=web_app_url)],
                [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = """✅ Вам открыт доступ к сигнальному боту TOWER BOT AI!

🎉 Поздравляем! Ваш депозит подтвержден администратором.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Теперь вы можете использовать весь функционал нашего бота и получать точные прогнозы с помощью искусственного интеллекта!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ЧТО ВАМ ДОСТУПНО:

• Получать точные сигналы для игры Tower Rush
• Использовать все возможности бота
• Получать прогнозы с высокой вероятностью успеха
• Доступ к веб-приложению для удобной игры
• Круглосуточная поддержка через бота
• Регулярные обновления и улучшения функционала

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 КАК ЭТО РАБОТАЕТ:

Наш бот основан на передовых технологиях искусственного интеллекта и анализирует множество параметров для выдачи наиболее точных сигналов. Каждый прогноз содержит информацию о количестве башен и вероятность успеха в процентах.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Ссылка на этого бота в Web-App:
https://tower-b0t-web.vercel.app/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 СОВЕТЫ:

• Используйте сигналы регулярно для лучших результатов
• Обращайте внимание на процент вероятности успеха
• При возникновении вопросов обращайтесь в поддержку

Используйте кнопки ниже для начала работы! 🚀

Желаем удачной игры и больших выигрышей! 🍀✨"""
            
            # Отправляем фото если указано
            if ACCESS_GRANTED_PHOTO:
                await context.bot.send_photo(
                    chat_id=target_user_id,
                    photo=ACCESS_GRANTED_PHOTO,
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=text,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {target_user_id}: {e}")
            
    except ValueError:
        await update.message.reply_text("❌ Неверный формат! Используйте: /add <user_id> <уровень_доступа>")


def _extract_1win_id_from_postback_text(text):
    """Извлекает ID пользователя 1win из текста постбэка."""
    if not text or not text.strip():
        return None
    if POSTBACK_USER_ID_REGEX:
        try:
            m = re.search(POSTBACK_USER_ID_REGEX, text.strip())
            return m.group(1).strip() if m and m.lastindex else None
        except Exception:
            pass
    m = re.search(r'\d+', text.strip())
    return m.group(0) if m else (text.strip() if len(text.strip()) < 100 else None)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста: если пользователь в режиме ожидания ID 1win — проверяем постбэки и выдаём доступ."""
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    since = db.get_awaiting_1win_id_since(user_id)
    if since is None:
        return
    if time.time() - since > AWAITING_1WIN_TIMEOUT:
        db.clear_awaiting_1win_id(user_id)
        await update.message.reply_text("⏰ Время ожидания вышло. Нажмите «Готово» в меню пополнения и снова отправьте ваш ID 1win.")
        return
    onewin_id = update.message.text.strip()
    db.clear_awaiting_1win_id(user_id)
    postback = db.get_unprocessed_postback_for_1win_id(onewin_id)
    if postback:
        postback_id, _, _, _, _ = postback
        db.mark_postback_processed(postback_id)
        db.give_access(user_id, 1)
        await _send_access_granted_message(context.bot, user_id)
        await update.message.reply_text("✅ Депозит найден в постбэках. Доступ открыт!")
    else:
        await update.message.reply_text(
            "❌ Депозит с таким ID 1win пока не найден в постбэках.\n\n"
            "Проверьте ID или подождите — постбэки приходят с задержкой. Можно снова нажать «Готово» и отправить ID позже."
        )


async def _send_access_granted_message(bot, chat_id):
    """Отправляет пользователю сообщение о выданном доступе (текст + кнопки)."""
    web_app_url = "https://tower-b0t-web.vercel.app/"
    keyboard = [
        [InlineKeyboardButton("🎮 Перейти к игре", url=web_app_url)],
        [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = """✅ Вам открыт доступ к сигнальному боту TOWER BOT AI!

🎉 Ваш депозит подтверждён по постбэку 1win.

🚀 Используйте кнопки ниже для перехода к игре и получения сигналов. Желаем удачи! 🍀"""
    if ACCESS_GRANTED_PHOTO:
        try:
            await bot.send_photo(chat_id=chat_id, photo=ACCESS_GRANTED_PHOTO, caption=text, reply_markup=reply_markup)
        except Exception:
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


def _extract_amount_from_postback_text(text):
    """Из постбэка вида sub1|country|Firstdep|amount или sub1|country|amount извлекает amount (доллары)."""
    if not text or '|' not in text:
        return None
    parts = text.strip().split('|')
    if len(parts) >= 2:
        last = parts[-1].strip()
        try:
            return float(last.replace(',', '.'))
        except ValueError:
            return None
    return None


async def handle_discussion_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сообщения из группы обсуждения канала — постбэки 1win. Форматы: sub1, sub1|country|Firstdep|amount, sub1|country|amount."""
    if not update.message or not update.message.text:
        return
    text = update.message.text
    onewin_id = _extract_1win_id_from_postback_text(text)
    if onewin_id:
        amount = _extract_amount_from_postback_text(text)
        db.add_postback(onewin_id, raw_text=text, amount=amount)
        logger.info(f"Постбэк сохранён: 1win_id={onewin_id}, amount={amount}")


async def setref_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /setref для обновления реферальной ссылки"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /setref <новая_ссылка>")
        return
    
    new_link = " ".join(context.args)
    db.update_referral_link(new_link)
    await update.message.reply_text(f"✅ Реферальная ссылка обновлена:\n{new_link}")


async def check_channel_subscription(bot: Bot, user_id: int) -> bool:
    """Проверка подписки пользователя на канал"""
    try:
        # Пробуем разные варианты получения информации
        try:
            # Сначала пробуем по username
            member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
            status = member.status
            logger.info(f"Пользователь {user_id} имеет статус: {status}")
            
            # Возвращаем True если пользователь подписан
            if status in ['member', 'administrator', 'creator']:
                return True
            elif status == 'left':
                return False
            else:
                # Если статус 'restricted' или 'kicked', считаем что не подписан
                logger.warning(f"Неожиданный статус: {status}")
                return False
                
        except Exception as e1:
            logger.error(f"Ошибка при проверке подписки через @{CHANNEL_USERNAME}: {e1}")
            # Пробуем без @
            try:
                member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
                status = member.status
                logger.info(f"Пользователь {user_id} имеет статус (без @): {status}")
                return status in ['member', 'administrator', 'creator']
            except Exception as e2:
                logger.error(f"Ошибка при проверке подписки без @: {e2}")
                # Если не получилось проверить - разрешаем доступ (чтобы не блокировать пользователей)
                logger.warning(f"Не удалось проверить подписку для {user_id}, разрешаем доступ")
                return True  # Разрешаем доступ если не можем проверить
                
    except Exception as e:
        logger.error(f"Критическая ошибка проверки подписки: {e}")
        # В случае критической ошибки разрешаем доступ
        return True


# Регистрация обработчиков
bot_application.add_handler(CommandHandler("start", start))
bot_application.add_handler(CommandHandler("add", add_command))
bot_application.add_handler(CommandHandler("setref", setref_command))
bot_application.add_handler(CallbackQueryHandler(button_handler))
bot_application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_text_message))
if CHANNEL_DISCUSSION_GROUP_ID:
    try:
        discussion_chat_id = int(CHANNEL_DISCUSSION_GROUP_ID)
        bot_application.add_handler(
            MessageHandler(filters.TEXT & filters.Chat(chat_id=discussion_chat_id), handle_discussion_group_message)
        )
        logger.info(f"Обработчик постбэков включён для группы обсуждения: {discussion_chat_id}")
    except ValueError:
        logger.warning("CHANNEL_DISCUSSION_GROUP_ID задан неверно, постбэки из канала не обрабатываются")


def get_bot_loop():
    """Возвращает общий event loop бота (работает в фоновом потоке)."""
    return _bot_loop


def _log_future_exception(fut):
    """Логирует исключение из фоновой задачи вебхука."""
    try:
        fut.result()
    except Exception:
        logger.exception("Ошибка при обработке апдейта (webhook)")


@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука — ставим обработку в общий event loop."""
    try:
        update = Update.de_json(request.get_json(force=True), bot_application.bot)
        loop = get_bot_loop()
        if loop is None:
            logger.error("Event loop бота ещё не запущен")
            return jsonify({'status': 'error', 'message': 'Bot loop not ready'}), 503
        future = asyncio.run_coroutine_threadsafe(bot_application.process_update(update), loop)
        future.add_done_callback(_log_future_exception)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.exception("Ошибка в webhook")
        return jsonify({'error': str(e)}), 500


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука (вызывается один раз) — выполняется в общем event loop."""
    webhook_url = request.args.get('url')
    if not webhook_url:
        base_url = request.url_root.rstrip('/')
        webhook_url = f"{base_url}/webhook"
    
    loop = get_bot_loop()
    if loop is None:
        return jsonify({'error': 'Bot loop not ready'}), 503
    
    async def set_wh():
        await bot_application.bot.set_webhook(url=webhook_url)
        return await bot_application.bot.get_webhook_info()
    
    try:
        future = asyncio.run_coroutine_threadsafe(set_wh(), loop)
        result = future.result(timeout=30)
        return jsonify({
            'status': 'success',
            'webhook_url': webhook_url,
            'webhook_info': result.to_dict()
        })
    except Exception as e:
        logger.exception("Ошибка set_webhook")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья бота"""
    return jsonify({'status': 'ok'})

@app.route('/info', methods=['GET'])
def info():
    """Информация о текущем домене"""
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    webhook_url = os.getenv('WEBHOOK_URL')
    port = os.getenv('PORT', '5000')
    
    info_data = {
        'port': port,
        'railway_domain': railway_domain,
        'webhook_url': webhook_url,
        'current_url': request.url_root.rstrip('/'),
        'webhook_endpoint': f"{request.url_root.rstrip('/')}/webhook"
    }
    return jsonify(info_data)


async def setup_webhook():
    """Установка вебхука при старте"""
    # Пробуем разные способы получить URL
    webhook_url = os.getenv('WEBHOOK_URL')
    
    # Если не указан явно, пробуем получить из Railway переменных
    if not webhook_url:
        railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_domain:
            # Убираем протокол если есть
            railway_domain = railway_domain.replace('https://', '').replace('http://', '')
            webhook_url = f"https://{railway_domain}/webhook"
            logger.info(f"Найден Railway домен: {railway_domain}")
    
    if webhook_url:
        try:
            await bot_application.bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook установлен: {webhook_url}")
        except Exception as e:
            logger.error(f"❌ Ошибка установки вебхука: {e}")
    else:
        logger.warning("⚠️ WEBHOOK_URL не указан, вебхук не установлен. Установите переменную WEBHOOK_URL или RAILWAY_PUBLIC_DOMAIN")


if __name__ == '__main__':
    # Инициализация БД
    db.init_db()
    
    # Проверяем режим работы: polling или webhook
    use_polling = os.getenv('USE_POLLING', 'false').lower() == 'true'
    
    if use_polling:
        # Режим polling - бот сам опрашивает Telegram
        logger.info("🤖 Запуск бота в режиме polling...")
        bot_application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
    else:
        # Режим webhook — один event loop в фоновом потоке, чтобы не было "Event loop is closed"
        _bot_loop = asyncio.new_event_loop()
        
        def run_loop():
            asyncio.set_event_loop(_bot_loop)

            async def init_and_webhook():
                await bot_application.initialize()
                await setup_webhook()

            _bot_loop.run_until_complete(init_and_webhook())
            _bot_loop.run_forever()
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        # Даём потоку время установить вебхук
        time.sleep(2)
        
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
