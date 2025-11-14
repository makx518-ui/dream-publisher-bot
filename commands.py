"""
Обработчики команд для управления ботом
"""
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import config
from bot import DreamOracleBot

# Глобальная переменная для хранения экземпляра бота
bot_instance = None
scheduler_instance = None


def set_bot_instance(bot, scheduler=None):
    """Устанавливает экземпляр бота для использования в командах"""
    global bot_instance, scheduler_instance
    bot_instance = bot
    scheduler_instance = scheduler


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    if config.ADMIN_USER_ID == 0:
        return True  # Если ID не установлен, разрешаем всем
    return user_id == config.ADMIN_USER_ID


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    welcome_text = f"""
🌙 **ОРАКУЛ СНОВ - Бот автопостинга**

Привет! Я автоматически публикую посты о снах и сновидениях в канал {config.CHANNEL_USERNAME}

📋 **Доступные команды:**
"""
    
    if is_admin(user_id):
        welcome_text += """
🔹 `/post_now` - создать пост сейчас (случайная тема)
🔹 `/post_custom [тема]` - создать пост на тему
🔹 `/status` - статус системы
🔹 `/next_post` - когда следующий пост
🔹 `/enable_auto` - включить автопостинг
🔹 `/disable_auto` - выключить автопостинг

⏰ **Автопостинг:** каждые {config.POST_INTERVAL_HOURS} часов
"""
    else:
        welcome_text += """
ℹ️ У вас нет прав для управления ботом.
📱 Подписывайтесь на канал: {config.CHANNEL_USERNAME}
"""
    
    await update.message.reply_text(welcome_text)


async def post_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /post_now - создать пост сейчас"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    await update.message.reply_text("⏳ Создаю пост... Это займёт ~30 секунд")
    
    try:
        if bot_instance:
            success = await bot_instance.create_and_publish_post()
            if success:
                await update.message.reply_text("✅ Пост успешно опубликован!")
            else:
                await update.message.reply_text("❌ Ошибка при создании поста")
        else:
            await update.message.reply_text("❌ Бот не инициализирован")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def post_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /post_custom [тема] - создать пост на тему"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    # Получаем тему из аргументов команды
    if not context.args:
        await update.message.reply_text(
            "ℹ️ Использование: /post_custom [тема]\n"
            "Например: /post_custom Юнг и архетипы в снах"
        )
        return
    
    topic = ' '.join(context.args)
    
    await update.message.reply_text(f"⏳ Создаю пост на тему: {topic}...\nЭто займёт ~30 секунд")
    
    try:
        if bot_instance:
            success = await bot_instance.publish_custom_post(topic)
            if success:
                await update.message.reply_text("✅ Пост успешно опубликован!")
            else:
                await update.message.reply_text("❌ Ошибка при создании поста")
        else:
            await update.message.reply_text("❌ Бот не инициализирован")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status - показать статус системы"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    status_text = f"""
📊 **СТАТУС СИСТЕМЫ**

📱 Канал: {config.CHANNEL_USERNAME}
⏰ Интервал постинга: каждые {config.POST_INTERVAL_HOURS} ч
"""
    
    if scheduler_instance and scheduler_instance.is_running:
        status_text += f"🟢 Автопостинг: ВКЛЮЧЕН\n"
        next_time = scheduler_instance.get_next_run_time()
        status_text += f"📅 Следующий пост: {next_time}"
    else:
        status_text += "🔴 Автопостинг: ВЫКЛЮЧЕН"
    
    await update.message.reply_text(status_text)


async def next_post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /next_post - когда следующий пост"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if scheduler_instance and scheduler_instance.is_running:
        next_time = scheduler_instance.get_next_run_time()
        await update.message.reply_text(f"📅 Следующий автоматический пост: {next_time}")
    else:
        await update.message.reply_text("ℹ️ Автопостинг выключен")


async def enable_auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /enable_auto - включить автопостинг"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if scheduler_instance:
        if scheduler_instance.is_running:
            await update.message.reply_text("ℹ️ Автопостинг уже включен")
        else:
            scheduler_instance.start()
            next_time = scheduler_instance.get_next_run_time()
            await update.message.reply_text(
                f"✅ Автопостинг включен!\n"
                f"📅 Следующий пост: {next_time}"
            )
    else:
        await update.message.reply_text("❌ Планировщик не инициализирован")


async def disable_auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /disable_auto - выключить автопостинг"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды")
        return
    
    if scheduler_instance:
        if not scheduler_instance.is_running:
            await update.message.reply_text("ℹ️ Автопостинг уже выключен")
        else:
            scheduler_instance.stop()
            await update.message.reply_text("✅ Автопостинг выключен")
    else:
        await update.message.reply_text("❌ Планировщик не инициализирован")
