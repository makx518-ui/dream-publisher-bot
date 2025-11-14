"""
Telegram бот для автоматического постинга в канал
Основной модуль системы
"""
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import config
from content_finder import ContentFinder
from groq_engine import GroqEngine

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class DreamOracleBot:
    """Основной класс бота Оракул Снов"""
    
    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN)
        self.content_finder = ContentFinder()
        self.groq_engine = GroqEngine()
        self.is_running = False
    
    async def create_and_publish_post(self, custom_topic: str = None) -> bool:
        """
        Создает и публикует пост в канал
        
        Args:
            custom_topic: опциональная тема для поста
        
        Returns:
            True если успешно, False если ошибка
        """
        try:
            print("\n" + "="*60)
            print("🚀 НАЧИНАЮ СОЗДАНИЕ ПОСТА")
            print("="*60)
            
            # Шаг 1: Ищем контент
            logger.info("📡 Поиск контента...")
            content_data = await self.content_finder.find_content(topic=custom_topic)
            
            if not content_data:
                logger.error("❌ Контент не найден, пропускаю публикацию")
                return False
            
            # Шаг 2: Генерируем пост через Groq
            logger.info("🤖 Генерация поста через Groq...")
            post_text = await self.groq_engine.generate_post(content_data)
            
            # Шаг 3: Публикуем в канал
            logger.info("📤 Публикация в канал...")
            message = await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=post_text,
                parse_mode=None,
                disable_web_page_preview=False
            )
            
            logger.info(f"✅ Пост опубликован! ID: {message.message_id}")
            logger.info(f"🔗 Ссылка: https://t.me/{config.CHANNEL_USERNAME.replace('@', '')}/{message.message_id}")
            
            print("="*60)
            print("✅ ПОСТ УСПЕШНО ОПУБЛИКОВАН!")
            print("="*60)
            
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Ошибка Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}", exc_info=True)
            return False
    
    async def publish_custom_post(self, user_request: str) -> bool:
        """
        Создает и публикует пост по запросу пользователя
        
        Args:
            user_request: текст запроса от пользователя
        
        Returns:
            True если успешно
        """
        try:
            print("\n" + "="*60)
            print(f"🎯 СОЗДАНИЕ КАСТОМНОГО ПОСТА")
            print(f"📝 Запрос: {user_request}")
            print("="*60)
            
            # Генерируем пост без поиска
            logger.info("🤖 Генерация кастомного поста...")
            post_text = await self.groq_engine.generate_custom_post(user_request)
            
            # Публикуем
            logger.info("📤 Публикация в канал...")
            message = await self.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=post_text,
                parse_mode=None
            )
            
            logger.info(f"✅ Кастомный пост опубликован! ID: {message.message_id}")
            
            print("="*60)
            print("✅ КАСТОМНЫЙ ПОСТ ОПУБЛИКОВАН!")
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации кастомного поста: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Тестирует подключение к Telegram и каналу"""
        try:
            print("\n🔍 Проверяю подключение...")
            
            # Проверяем бота
            bot_info = await self.bot.get_me()
            print(f"✅ Бот подключен: @{bot_info.username}")
            
            # Проверяем права в канале
            chat = await self.bot.get_chat(config.CHANNEL_ID)
            print(f"✅ Канал найден: {chat.title}")
            
            # Проверяем права администратора
            bot_member = await self.bot.get_chat_member(config.CHANNEL_ID, bot_info.id)
            if bot_member.status in ['administrator', 'creator']:
                print(f"✅ Бот является администратором канала")
            else:
                print(f"⚠️ Внимание: бот не администратор! Статус: {bot_member.status}")
            
            return True
            
        except TelegramError as e:
            print(f"❌ Ошибка подключения: {e}")
            return False


# Основная функция для тестового запуска
async def main():
    """Тестовый запуск системы"""
    print("\n" + "="*60)
    print("🌙 ОРАКУЛ СНОВ - СИСТЕМА АВТОПОСТИНГА")
    print("="*60)
    
    # Проверяем конфигурацию
    try:
        config.validate_config()
        print("✅ Конфигурация корректна")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создаем бота
    bot = DreamOracleBot()
    
    # Тестируем подключение
    if not await bot.test_connection():
        print("❌ Не удалось подключиться к Telegram")
        return
    
    # Создаем и публикуем тестовый пост
    print("\n📝 Создаю и публикую тестовый пост...")
    success = await bot.create_and_publish_post()
    
    if success:
        print("\n✨ Тестовый запуск завершен успешно!")
    else:
        print("\n❌ Ошибка при создании поста")


if __name__ == '__main__':
    asyncio.run(main())
