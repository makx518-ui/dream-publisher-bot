"""
Планировщик автоматического постинга
Запускает создание и публикацию постов по расписанию
"""
import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
import config
from bot import DreamOracleBot

logger = logging.getLogger(__name__)


class PostScheduler:
    """Планировщик автоматических постов"""
    
    def __init__(self):
        self.bot = DreamOracleBot()
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
        self.is_running = False
    
    async def scheduled_post(self):
        """Функция, которая вызывается по расписанию"""
        try:
            logger.info("⏰ Время для автопоста!")
            await self.bot.create_and_publish_post()
        except Exception as e:
            logger.error(f"❌ Ошибка в scheduled_post: {e}", exc_info=True)
    
    def start(self):
        """Запускает планировщик"""
        if self.is_running:
            logger.warning("⚠️ Планировщик уже запущен")
            return
        
        # Добавляем задачу на автопостинг
        self.scheduler.add_job(
            self.scheduled_post,
            trigger=IntervalTrigger(hours=config.POST_INTERVAL_HOURS),
            id='auto_post',
            name='Автоматический постинг',
            replace_existing=True
        )
        
        # Запускаем планировщик
        self.scheduler.start()
        self.is_running = True
        
        # Информация о следующем запуске
        next_run = self.scheduler.get_job('auto_post').next_run_time
        
        logger.info("✅ Планировщик запущен!")
        logger.info(f"⏰ Интервал: каждые {config.POST_INTERVAL_HOURS} часов")
        logger.info(f"📅 Следующий пост: {next_run.strftime('%d.%m.%Y %H:%M:%S')}")
    
    def stop(self):
        """Останавливает планировщик"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("⏹️ Планировщик остановлен")
    
    def get_next_run_time(self) -> str:
        """Возвращает время следующего запуска"""
        if not self.is_running:
            return "Планировщик не запущен"
        
        job = self.scheduler.get_job('auto_post')
        if job:
            next_run = job.next_run_time
            return next_run.strftime('%d.%m.%Y %H:%M:%S')
        return "Неизвестно"


async def run_scheduler():
    """Запуск планировщика в бесконечном цикле"""
    print("\n" + "="*60)
    print("🌙 ОРАКУЛ СНОВ - АВТОПОСТИНГ ЗАПУЩЕН")
    print("="*60)
    
    # Проверяем конфигурацию
    try:
        config.validate_config()
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Проверяем, включен ли автопостинг
    if not config.AUTO_POST_ENABLED:
        print("⚠️ Автопостинг отключен в конфигурации!")
        print("💡 Установите AUTO_POST_ENABLED=true в .env файле")
        return
    
    # Создаем планировщик
    scheduler = PostScheduler()
    
    # Тестируем подключение
    print("\n🔍 Проверяю подключение...")
    if not await scheduler.bot.test_connection():
        print("❌ Не удалось подключиться к Telegram")
        return
    
    # Запускаем планировщик
    print("\n🚀 Запускаю планировщик...")
    scheduler.start()
    
    print("\n" + "="*60)
    print("✅ СИСТЕМА РАБОТАЕТ!")
    print("="*60)
    print(f"📱 Канал: {config.CHANNEL_USERNAME}")
    print(f"⏰ Интервал: каждые {config.POST_INTERVAL_HOURS} часов")
    print(f"📅 Следующий пост: {scheduler.get_next_run_time()}")
    print("\n💡 Нажмите Ctrl+C для остановки")
    print("="*60)
    
    # Пропускаем создание первого поста для избежания проблем с кодировкой
    print("\n⏳ Система в режиме ожидания...")
    print("📅 Первый автоматический пост будет создан по расписанию")
    
    # Держим программу запущенной
    try:
        while True:
            await asyncio.sleep(60)  # Проверяем каждую минуту
            
            # Показываем статус каждый час
            if datetime.now().minute == 0:
                print(f"\n⏰ {datetime.now().strftime('%H:%M')} - Система работает")
                print(f"📅 Следующий пост: {scheduler.get_next_run_time()}")
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Получен сигнал остановки...")
        scheduler.stop()
        print("✅ Планировщик остановлен")
        print("👋 До встречи!")


if __name__ == '__main__':
    asyncio.run(run_scheduler())