"""
Движок генерации контента через Groq AI
Превращает найденные материалы в уникальные посты
"""
import asyncio
from groq import AsyncGroq
import config

class GroqEngine:
    """Класс для генерации контента через Groq AI"""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
    
    async def generate_post(self, content_data: dict) -> str:
        """
        Генерирует пост на основе найденного контента
        
        Args:
            content_data: словарь с данными контента
                - topic: тема
                - title: заголовок
                - description: описание
                - content: полный текст (опционально)
                - url: ссылка на источник
        
        Returns:
            Сгенерированный пост
        """
        try:
            print(f"\n🤖 Генерирую пост через Groq...")
            
            # Формируем промпт для Groq
            prompt = self._create_prompt(content_data)
            
            # Отправляем запрос в Groq
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": config.POST_STYLE_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,
                max_tokens=800,
                top_p=1.0
            )
            
            # Извлекаем текст
            generated_text = response.choices[0].message.content.strip()
            
            # Добавляем ссылку на источник внизу
            if content_data.get('url'):
                generated_text += f"\n\n🔗 Источник: {content_data['url']}"
            
            print(f"✅ Пост сгенерирован! Длина: {len(generated_text)} символов")
            
            return generated_text
            
        except Exception as e:
            print(f"❌ Ошибка генерации через Groq: {e}")
            raise
    
    def _create_prompt(self, content_data: dict) -> str:
        """Создает промпт для Groq на основе контента"""
        
        topic = content_data.get('topic', 'сновидения')
        title = content_data.get('title', '')
        description = content_data.get('description', '')
        content = content_data.get('content', description)
        
        prompt = f"""
На основе этого материала создай интересный пост для канала "Оракул Снов":

ТЕМА: {topic}

ЗАГОЛОВОК: {title}

СОДЕРЖАНИЕ:
{content[:1500]}

ЗАДАЧА:
1. Создай захватывающий пост на русском языке (200-400 слов)
2. Начни с мистического вступления с эмодзи
3. Объясни научные факты простым языком
4. Добавь эзотерическую интерпретацию
5. Закончи практическим советом или вопросом для размышления
6. Используй эмодзи для структуры: 🌙 💭 🔮 ✨ 🧠 📚

СТИЛЬ: Сочетай научность и мистику, будь увлекательным!

НЕ указывай источник в тексте поста (ссылка добавится автоматически).
"""
        return prompt
    
    async def generate_custom_post(self, user_request: str) -> str:
        """
        Генерирует пост по запросу пользователя (без поиска контента)
        
        Args:
            user_request: запрос от пользователя
        
        Returns:
            Сгенерированный пост
        """
        try:
            print(f"\n🤖 Генерирую пост по запросу: {user_request[:50]}...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": config.POST_STYLE_PROMPT
                    },
                    {
                        "role": "user",
                        "content": f"""
Создай пост для канала "Оракул Снов" на тему:

{user_request}

Требования:
- 200-400 слов на русском языке
- Используй эмодзи
- Сочетай научные факты и эзотерику
- Будь увлекательным и информативным
"""
                    }
                ],
                temperature=0.9,
                max_tokens=800,
                top_p=1.0
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            print(f"✅ Кастомный пост сгенерирован!")
            
            return generated_text
            
        except Exception as e:
            print(f"❌ Ошибка генерации кастомного поста: {e}")
            raise


# Тестирование модуля
async def test_groq_engine():
    """Тестовый запуск генерации"""
    engine = GroqEngine()
    
    # Тестовые данные
    test_content = {
        'topic': 'осознанные сновидения',
        'title': 'New Study Reveals Brain Activity During Lucid Dreams',
        'description': 'Scientists discovered increased activity in the prefrontal cortex during lucid dreaming...',
        'content': 'Research shows that lucid dreamers have more gray matter in their frontopolar cortex...',
        'url': 'https://example.com/lucid-dreams-study'
    }
    
    print("📝 Тестирую генерацию поста с контентом...")
    post = await engine.generate_post(test_content)
    
    print("\n" + "="*60)
    print("📰 СГЕНЕРИРОВАННЫЙ ПОСТ:")
    print("="*60)
    print(post)
    print("="*60)
    
    print("\n📝 Тестирую кастомную генерацию...")
    custom_post = await engine.generate_custom_post(
        "Расскажи о символике воды в снах с точки зрения Юнга"
    )
    
    print("\n" + "="*60)
    print("📰 КАСТОМНЫЙ ПОСТ:")
    print("="*60)
    print(custom_post)
    print("="*60)


if __name__ == '__main__':
    asyncio.run(test_groq_engine())
