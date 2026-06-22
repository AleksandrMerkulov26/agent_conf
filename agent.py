#!/usr/bin/env python3
# agent.py - Главный оркестратор

import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Импортируем все модули
from config import Config
from logger import Logger
from confluence_client import ConfluenceClient
from gigachat_client import GigaChatClient
from entity_resolver import EntityResolver
from cache_manager import CacheManager
from link_follower import LinkFollower
from ambiguity_handler import AmbiguityHandler
from slack_notifier import SlackNotifier


class AgentFinder:
    """Главный класс агента-поисковика"""
    
    def __init__(self):
        # 1. Загружаем настройки
        try:
            self.config = Config.from_env()
            self.config.validate()
        except ValueError as e:
            print(f"❌ Ошибка конфигурации: {e}")
            print("\n📝 Инструкция:")
            print("1. Скопируй .env.example в .env")
            print("2. Заполни .env своими данными (токены, URL)")
            print("3. Запусти снова")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Неожиданная ошибка при загрузке конфигурации: {e}")
            sys.exit(1)
        
        # 2. Настраиваем логирование
        self.logger = Logger(
            log_file=self.config.log_file,
            log_level=self.config.log_level
        )
        self.logger.info("🚀 Агент-поисковик запущен")
        self.logger.info(f"📋 Конфигурация загружена: {self.config.confluence_url}")
        
        # 3. Инициализируем все модули
        self.logger.debug("Инициализация модулей...")
        self.confluence = ConfluenceClient(self.config)
        self.gigachat = GigaChatClient(self.config)
        self.entity_resolver = EntityResolver()
        self.cache_manager = CacheManager(self.config.cache_file)
        self.link_follower = LinkFollower(self.confluence)
        self.ambiguity_handler = AmbiguityHandler(self.gigachat)
        self.slack = SlackNotifier(self.config) if self.config.slack_webhook_url else None
        
        self.logger.success("Все модули инициализированы")
    
    def find_owner(self, user_input: str) -> Dict[str, Any]:
        """
        Основной метод поиска владельца
        
        Args:
            user_input: Строка от пользователя (URL, лог, описание)
        
        Returns:
            Dict с информацией о владельце
        """
        start_time = time.time()
        self.logger.info(f"🔍 Поиск по запросу: {user_input[:100]}...")
        
        # ---- Шаг 1: Проверяем кеш ----
        cached_result = self.cache_manager.get(user_input)
        if cached_result:
            self.logger.success("📦 Найдено в кеше! (использовано закешированный результат)")
            cached_result["from_cache"] = True
            return cached_result
        
        # ---- Шаг 2: Извлекаем ключевые слова ----
        keywords = self.entity_resolver.extract_keywords(user_input)
        self.logger.info(f"🔑 Ключевые слова: {keywords}")
        
        if not keywords:
            self.logger.warning("⚠️ Не удалось извлечь ключевые слова из запроса")
            # Пробуем использовать весь запрос как поисковый
            keywords = [user_input]
        
        # ---- Шаг 3: Ищем в Confluence ----
        pages = self.confluence.search(keywords, limit=self.config.max_pages_to_analyze)
        
        if not pages:
            self.logger.warning("❌ Страницы в Confluence не найдены")
            # Пробуем пройти по ссылкам
            self.logger.info("🔄 Пытаемся найти через ссылки...")
            pages = self.link_follower.find_by_links(keywords, depth=self.config.follow_links_depth)
        
        if not pages:
            self.logger.error("❌ Не удалось найти ни одной страницы")
            return {
                "found": False,
                "error": "Страницы в Confluence не найдены",
                "query": user_input,
                "keywords": keywords
            }
        
        self.logger.info(f"📚 Найдено {len(pages)} страниц, анализирую...")
        
        # ---- Шаг 4: Загружаем содержимое страниц ----
        page_contents = []
        for page in pages[:self.config.max_pages_to_analyze]:
            try:
                content = self.confluence.get_page_content(page["id"])
                # Обрезаем длинный текст
                if len(content) > self.config.max_content_length:
                    content = content[:self.config.max_content_length] + "..."
                
                page_contents.append({
                    "title": page["title"],
                    "url": page["url"],
                    "id": page["id"],
                    "content": content
                })
            except Exception as e:
                self.logger.warning(f"⚠️ Не удалось загрузить страницу {page['title']}: {e}")
        
        if not page_contents:
            self.logger.error("❌ Не удалось загрузить содержимое страниц")
            return {
                "found": False,
                "error": "Не удалось загрузить содержимое страниц",
                "query": user_input
            }
        
        # ---- Шаг 5: Анализируем через нейросеть ----
        self.logger.info("🧠 Отправка запроса в GigaChat...")
        analysis = self.gigachat.find_owner(user_input, page_contents)
        
        if not analysis or analysis.get("team_name") == "НЕ НАЙДЕНО":
            self.logger.warning("❌ Нейросеть не нашла владельца")
            # Пробуем разрешить неоднозначность
            if len(page_contents) > 1:
                self.logger.info("🤔 Пробуем разрешить неоднозначность...")
                analysis = self.ambiguity_handler.handle(page_contents, user_input)
        
        # ---- Шаг 6: Проверяем результат ----
        if not analysis or analysis.get("team_name") == "НЕ НАЙДЕНО":
            self.logger.error("❌ Владелец не найден")
            result = {
                "found": False,
                "error": "Владелец не найден в документации",
                "query": user_input,
                "pages_found": len(page_contents),
                "pages": [{"title": p["title"], "url": p["url"]} for p in page_contents]
            }
        else:
            # Добавляем информацию о страницах
            analysis["pages_found"] = len(page_contents)
            analysis["pages"] = [{"title": p["title"], "url": p["url"]} for p in page_contents]
            analysis["found"] = True
            analysis["from_cache"] = False
            
            # Сохраняем в кеш
            self.cache_manager.set(user_input, analysis)
            self.logger.success(f"✅ Найден владелец: {analysis.get('team_name')}")
            
            # Отправляем в Slack, если настроено
            if self.slack and self.config.auto_slack_ask:
                self.slack.send_report(analysis)
                self.logger.info("💬 Отчет отправлен в Slack")
            
            result = analysis
        
        # Логируем время выполнения
        elapsed = time.time() - start_time
        self.logger.info(f"⏱️ Поиск занял {elapsed:.2f} секунд")
        
        return result
    
    def print_result(self, result: Dict[str, Any]):
        """Красиво выводит результат в консоль"""
        print("\n" + "="*60)
        print("🔍 РЕЗУЛЬТАТ ПОИСКА")
        print("="*60)
        
        if result.get("found"):
            print(f"👤 Команда-владелец: {result.get('team_name', 'Не указано')}")
            print(f"📧 Контакт: {result.get('contact', 'Не указан')}")
            print(f"💬 Slack: {result.get('slack', 'Не указан')}")
            print(f"📄 Основная страница: {result.get('main_page_url', 'Не найдена')}")
            print(f"📊 Уверенность: {result.get('confidence', 'Не указана')}")
            
            if result.get("from_cache"):
                print("\n📦 Результат взят из кеша (быстрый ответ)")
            else:
                print(f"\n📚 Проанализировано страниц: {result.get('pages_found', 0)}")
                print("📋 Найденные страницы:")
                for page in result.get("pages", [])[:3]:
                    print(f"   - {page.get('title')}: {page.get('url')}")
            
            print("\n✅ Владелец найден успешно!")
        else:
            print(f"❌ {result.get('error', 'Владелец не найден')}")
            print(f"📝 Запрос: {result.get('query', 'Не указан')}")
            
            if result.get("pages"):
                print("\n📋 Найденные страницы (возможно, там есть информация):")
                for page in result.get("pages", [])[:5]:
                    print(f"   - {page.get('title')}: {page.get('url')}")
        
        print("="*60)
        
        # Если владелец не найден, предлагаем отправить запрос в Slack
        if not result.get("found") and self.slack:
            print("\n💡 Хочешь отправить вопрос в Slack-канал?")
            response = input("(y/n): ").lower()
            if response == 'y':
                team_channel = input("Введите Slack-канал (например, #tech-support): ")
                self.slack.ask_team(
                    team_channel,
                    f"Кто владеет сервисом/системой: {result.get('query', 'Неизвестно')}?",
                    f"Найдены страницы: {', '.join([p['title'] for p in result.get('pages', [])[:3]])}"
                )
                print("✅ Вопрос отправлен!")


def main():
    """Точка входа в программу"""
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("❌ Ошибка: не указан запрос для поиска")
        print("\n📝 Использование:")
        print("  python agent.py 'текст для поиска'")
        print("\n📌 Примеры:")
        print("  python agent.py 'https://api.payments.internal/v2/status'")
        print("  python agent.py 'payments timeout error'")
        print("  python agent.py 'сервис авторизации'")
        sys.exit(1)
    
    # Объединяем все аргументы в один запрос
    user_input = " ".join(sys.argv[1:])
    
    # Создаем агента и ищем
    agent = AgentFinder()
    result = agent.find_owner(user_input)
    agent.print_result(result)


if __name__ == "__main__":
    main()
