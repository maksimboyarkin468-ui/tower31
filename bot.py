import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
from database import Database
from config import BOT_TOKEN, ADMIN_ID, CHANNEL_USERNAME, SUPPORT_LINK, DEFAULT_REFERRAL_LINK

# РќР°СЃС‚СЂРѕР№РєР° Р»РѕРіРёСЂРѕРІР°РЅРёСЏ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db = Database()

# РЎРѕР·РґР°РµРј РїСЂРёР»РѕР¶РµРЅРёРµ Р±РѕС‚Р°
bot_application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """РћР±СЂР°Р±РѕС‚С‡РёРє РєРѕРјР°РЅРґС‹ /start"""
    user_id = update.effective_user.id
    
    # Р”РѕР±Р°РІР»СЏРµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ РІ Р‘Р”
    db.add_user(user_id, update.effective_user.username)
    
    # Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ
    keyboard = [
        [InlineKeyboardButton("рџЋЇ РџРѕР»СѓС‡РёС‚СЊ СЃРёРіРЅР°Р»", callback_data="get_signal")],
        [InlineKeyboardButton("рџ’¬ РџРѕРґРґРµСЂР¶РєР°", url=SUPPORT_LINK)],
        [InlineKeyboardButton("вљ™пёЏ РџР°РЅРµР»СЊ Р°РґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂР°", callback_data="admin_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """рџЏ  Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ РІ РіР»Р°РІРЅРѕРµ РјРµРЅСЋ!

Р’С‹ РЅР°С…РѕРґРёС‚РµСЃСЊ РІ СЃРёРіРЅР°Р»СЊРЅРѕРј Р±РѕС‚Рµ TOWER BOT AI рџЋЇ

рџ“Љ Р¤СѓРЅРєС†РёРѕРЅР°Р» Р±РѕС‚Р°:
вЂў РџРѕР»СѓС‡РµРЅРёРµ С‚РѕС‡РЅС‹С… СЃРёРіРЅР°Р»РѕРІ РґР»СЏ РёРіСЂС‹ Tower Rush
вЂў РђРЅР°Р»РёР· СЃ РїРѕРјРѕС‰СЊСЋ РёСЃРєСѓСЃСЃС‚РІРµРЅРЅРѕРіРѕ РёРЅС‚РµР»Р»РµРєС‚Р°
вЂў РџСЂРѕРіРЅРѕР·РёСЂРѕРІР°РЅРёРµ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ СЃ РІС‹СЃРѕРєРѕР№ РІРµСЂРѕСЏС‚РЅРѕСЃС‚СЊСЋ
вЂў РЈРґРѕР±РЅС‹Р№ РёРЅС‚РµСЂС„РµР№СЃ Рё Р±С‹СЃС‚СЂС‹Р№ РґРѕСЃС‚СѓРї Рє СЃРёРіРЅР°Р»Р°Рј

Р’С‹Р±РµСЂРёС‚Рµ РґРµР№СЃС‚РІРёРµ РёР· РјРµРЅСЋ РЅРёР¶Рµ рџ‘‡"""
    
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
        # Показываем окно ожидания
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = """⏳ Ожидание подтверждения доступа

✅ Ваша заявка на получение доступа к сигналам принята!

👨‍💼 Наш администратор проверит ваше пополнение и выдаст доступ в ближайшее время.

⏰ Обычно это занимает несколько минут.

🔔 Вы получите уведомление, как только доступ будет активирован!

Спасибо за терпение 🙏"""
        
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
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)


async def handle_admin_panel(query, context):
    """Панель администратора"""
    user_id = query.from_user.id
    
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
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {target_user_id}: {e}")
            
    except ValueError:
        await update.message.reply_text("❌ Неверный формат! Используйте: /add <user_id> <уровень_доступа>")


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


@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука"""
    update = Update.de_json(request.get_json(force=True), bot_application.bot)
    asyncio.create_task(bot_application.process_update(update))
    return jsonify({'status': 'ok'})


@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука (вызывается один раз)"""
    webhook_url = request.args.get('url')
    if not webhook_url:
        return jsonify({'error': 'Не указан URL'}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def set_wh():
        await bot_application.bot.set_webhook(url=webhook_url)
        return await bot_application.bot.get_webhook_info()
    
    result = loop.run_until_complete(set_wh())
    loop.close()
    
    return jsonify(result.to_dict())


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья бота"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # Инициализация БД
    db.init_db()
    
    # Запуск Flask приложения
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
