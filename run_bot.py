"""
🌙 ОРАКУЛ СНОВ - Главный файл запуска с командами
Версия 2.0 - с управлением через Telegram
"""
import asyncio
import sys
import logging
from telegram.ext import Application, CommandHandler
from bot import DreamOracleBot
from scheduler import PostScheduler
import commands
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска бота с командами"""
    
    print("\n" + "="*60)
    print("🌙 ОРАКУЛ СНОВ - СИСТЕМА АВТОПОСТИНГА v2.0")
    print("="*60)
    
    # Проверяем конфигурацию
    try:
        config.validate_config()
        print("✅ Конфигурация корректна")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создаем экземпляры бота и планировщика
    bot = DreamOracleBot()
    scheduler = PostScheduler()
    
    # Передаем экземпляры в модуль команд
    commands.set_bot_instance(bot, scheduler)
    
    # Проверяем подключение
    print("\n🔍 Проверяю подключение...")
    if not await bot.test_connection():
        print("❌ Не удалось подключиться к Telegram")
        return
    
    # Создаем приложение для обработки команд
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler('start', commands.start_command))
    application.add_handler(CommandHandler('post_now', commands.post_now_command))
    application.add_handler(CommandHandler('post_custom', commands.post_custom_command))
    application.add_handler(CommandHandler('status', commands.status_command))
    application.add_handler(CommandHandler('next_post', commands.next_post_command))
    application.add_handler(CommandHandler('enable_auto', commands.enable_auto_command))
    application.add_handler(CommandHandler('disable_auto', commands.disable_auto_command))
    
    print("\n✅ Команды управления зарегистрированы:")
    print("   /start - информация о боте")
    print("   /post_now - создать пост сейчас")
    print("   /post_custom [тема] - создать пост на тему")
    print("   /status - статус системы")
    print("   /next_post - когда следующий пост")
    print("   /enable_auto - включить автопостинг")
    print("   /disable_auto - выключить автопостинг")
    
    # Автоматически запускаем автопостинг если включен в настройках
    print("\n" + "="*60)
    if config.AUTO_POST_ENABLED:
        scheduler.start()
        print(f"✅ Автопостинг запущен автоматически!")
        print(f"⏰ Интервал: каждые {config.POST_INTERVAL_HOURS} часов")
        print(f"📅 Следующий пост: {scheduler.get_next_run_time()}")
    else:
        print(f"ℹ️ Автопостинг выключен (AUTO_POST_ENABLED=false)")
        print(f"💡 Для включения используйте команду /enable_auto")
    
    print("\n" + "="*60)
    print("✅ БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
    print("="*60)
    print(f"\n📱 Канал: {config.CHANNEL_USERNAME}")
    print(f"🤖 Управление: напишите боту /start в личку")
    
    if config.ADMIN_USER_ID == 0:
        print("\n⚠️  ВНИМАНИЕ: ADMIN_USER_ID не установлен!")
        print("   Для получения своего ID:")
        print("   1. Напишите боту /start")
        print("   2. Посмотрите в логи - там будет ваш ID")
        print("   3. Добавьте его в .env файл")
    
    print("\n💡 Для остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    # Запускаем бота
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    try:
        # Держим бота запущенным
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\n\n⏹️ Получен сигнал остановки...")
    finally:
        # Останавливаем всё
        if scheduler.is_running:
            scheduler.stop()
        await application.stop()
        await application.shutdown()
        print("✅ Бот остановлен")
        print("👋 До встречи!")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)