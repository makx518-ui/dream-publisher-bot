"""
Модуль поиска контента из различных источников
Использует: NewsAPI, DuckDuckGo, RSS-фиды
"""
import asyncio
import random
from typing import List, Dict, Optional
import feedparser
from newsapi import NewsApiClient
from duckduckgo_search import DDGS
import config

class ContentFinder:
    """Класс для поиска контента о снах и сновидениях"""
    
    def __init__(self):
        self.news_api = None
        if config.NEWS_API_KEY:
            try:
                self.news_api = NewsApiClient(api_key=config.NEWS_API_KEY)
            except Exception as e:
                print(f"⚠️ NewsAPI недоступен: {e}")
    
    async def search_news_api(self, query: str, max_results: int = 3) -> List[Dict]:
        """Поиск через NewsAPI"""
        if not self.news_api:
            return []
        
        try:
            print(f"🔍 Ищу в NewsAPI: {query}")
            
            # Поиск статей
            response = self.news_api.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=max_results
            )
            
            articles = []
            for article in response.get('articles', [])[:max_results]:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'published': article.get('publishedAt', '')
                })
            
            print(f"✅ NewsAPI: найдено {len(articles)} статей")
            return articles
            
        except Exception as e:
            print(f"❌ Ошибка NewsAPI: {e}")
            return []
    
    async def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Поиск через DuckDuckGo"""
        try:
            print(f"🔍 Ищу в DuckDuckGo: {query}")
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'description': result.get('body', ''),
                        'url': result.get('href', ''),
                        'source': 'DuckDuckGo'
                    })
            
            print(f"✅ DuckDuckGo: найдено {len(results)} результатов")
            return results
            
        except Exception as e:
            print(f"❌ Ошибка DuckDuckGo: {e}")
            return []
    
    async def parse_rss_feeds(self, max_per_feed: int = 2) -> List[Dict]:
        """Парсинг RSS-фидов"""
        try:
            print(f"🔍 Парсю RSS-фиды: {len(config.RSS_FEEDS)} источников")
            
            all_articles = []
            
            for feed_url in config.RSS_FEEDS:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:max_per_feed]:
                        all_articles.append({
                            'title': entry.get('title', ''),
                            'description': entry.get('summary', ''),
                            'url': entry.get('link', ''),
                            'source': feed.feed.get('title', 'RSS Feed'),
                            'published': entry.get('published', '')
                        })
                    
                except Exception as e:
                    print(f"⚠️ Ошибка парсинга {feed_url}: {e}")
                    continue
            
            print(f"✅ RSS: найдено {len(all_articles)} статей")
            return all_articles
            
        except Exception as e:
            print(f"❌ Ошибка RSS: {e}")
            return []
    
    async def find_content(self, topic: Optional[str] = None) -> Dict:
        """
        Главный метод: ищет контент по теме
        Возвращает лучший найденный материал
        """
        # Выбираем случайную тему, если не указана
        if not topic and config.SEARCH_TOPICS:
            topic = random.choice(config.SEARCH_TOPICS)
        
        if not topic:
            topic = "dreams and sleep science"
        
        print(f"\n🎯 Ищу контент по теме: {topic}")
        
        # Запускаем все поиски параллельно
        results = await asyncio.gather(
            self.search_news_api(topic),
            self.search_duckduckgo(topic),
            self.parse_rss_feeds(),
            return_exceptions=True
        )
        
        # Собираем все результаты
        all_content = []
        for result in results:
            if isinstance(result, list):
                all_content.extend(result)
        
        if not all_content:
            print("❌ Контент не найден!")
            return None
        
        # Выбираем случайный материал
        selected = random.choice(all_content)
        
        print(f"✅ Выбран материал: {selected['title'][:50]}...")
        print(f"📍 Источник: {selected['source']}")
        
        return {
            'topic': topic,
            'title': selected['title'],
            'description': selected['description'],
            'content': selected.get('content', selected['description']),
            'url': selected['url'],
            'source': selected['source']
        }


# Тестирование модуля
async def test_content_finder():
    """Тестовый запуск поиска"""
    finder = ContentFinder()
    content = await finder.find_content()
    
    if content:
        print("\n" + "="*60)
        print("📰 НАЙДЕННЫЙ КОНТЕНТ:")
        print("="*60)
        print(f"🎯 Тема: {content['topic']}")
        print(f"📌 Заголовок: {content['title']}")
        print(f"📝 Описание: {content['description'][:200]}...")
        print(f"🔗 URL: {content['url']}")
        print(f"📍 Источник: {content['source']}")
        print("="*60)
    else:
        print("❌ Контент не найден")


if __name__ == '__main__':
    asyncio.run(test_content_finder())
