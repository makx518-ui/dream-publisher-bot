"""
Конфигурация системы автопостинга
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram настройки
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))  # ID администратора для команд

# Groq настройки
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = "llama-3.3-70b-versatile"

# NewsAPI настройки
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Настройки автопостинга
AUTO_POST_ENABLED = os.getenv('AUTO_POST_ENABLED', 'true').lower() == 'true'
POST_INTERVAL_HOURS = int(os.getenv('POST_INTERVAL_HOURS', '8'))

# Темы для поиска
SEARCH_TOPICS = os.getenv('SEARCH_TOPICS', '').split(',')
SEARCH_TOPICS = [topic.strip() for topic in SEARCH_TOPICS if topic.strip()]

# Язык контента
CONTENT_LANGUAGE = os.getenv('CONTENT_LANGUAGE', 'ru')

# RSS фиды научных источников
RSS_FEEDS = [
    'https://www.sciencedaily.com/rss/mind_brain/sleep.xml',
    'https://www.sciencedaily.com/rss/mind_brain/dreams.xml',
    'http://feeds.feedburner.com/PsychologyToday/blog/dream-factory',
]

# Стиль генерации постов
POST_STYLE_PROMPT = """
Ты - Оракул Снов, мистический гид в мире сновидений. 
Твой стиль: сочетание научных фактов с эзотерической мудростью.
Используй эмодзи, создавай атмосферу тайны, но опирайся на реальные исследования.
Пиши на русском языке, делай посты интересными и вовлекающими.
"""

# Проверка наличия всех необходимых ключей
def validate_config():
    """Проверяет наличие всех необходимых настроек"""
    required_vars = {
        'BOT_TOKEN': BOT_TOKEN,
        'CHANNEL_ID': CHANNEL_ID,
        'GROQ_API_KEY': GROQ_API_KEY,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(f"Отсутствуют обязательные переменные: {', '.join(missing)}")
    
    return True

if __name__ == '__main__':
    try:
        validate_config()
        print("✅ Конфигурация корректна!")
        print(f"📱 Канал: {CHANNEL_USERNAME}")
        print(f"🤖 Автопостинг: {'Включен' if AUTO_POST_ENABLED else 'Выключен'}")
        print(f"⏰ Интервал: каждые {POST_INTERVAL_HOURS} часов")
        print(f"🔍 Темы поиска: {len(SEARCH_TOPICS)}")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")