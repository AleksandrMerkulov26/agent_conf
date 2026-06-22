# agent.py - обновленная версия с СберЧат

import sys
import time
from typing import Dict, Any

from config import Config
from logger import Logger
from confluence_client import ConfluenceClient
from gigachat_client import GigaChatClient
from entity_resolver import EntityResolver
from cache_manager import CacheManager
from link_follower import LinkFollower
from ambiguity_handler import AmbiguityHandler
from sberchat_notifier import SberChatNotifier  # ← Заменили Slack на СберЧат


class AgentFinder:
    def __init__(self):
        # ... (загрузка конфига и инициализация модулей такая же)
        # ...
        
        # Инициализируем СберЧат, если есть webhook
        self.sberchat = SberChatNotifier(self.config) if self.config.sberchat_webhook_url else None
        
        # ... остальной код

    def find_owner(self, user_input: str) -> Dict[str, Any]:
        # ... (весь код поиска такой же)
        # ...
        
        # Когда владелец найден, отправляем отчет в СберЧат
        if result.get("found") and self.sberchat and self.config.auto_sberchat_ask:
            self.sberchat.send_report(result)
            self.logger.info("💬 Отчет отправлен в СберЧат")
        
        return result

    def print_result(self, result: Dict[str, Any]):
        # ... (вывод в консоль)
        # ...
        
        # Если владелец не найден, предлагаем отправить запрос в СберЧат
        if not result.get("found") and self.sberchat:
            print("\n💡 Хочешь отправить вопрос в СберЧат?")
            response = input("(y/n): ").lower()
            if response == 'y':
                team_channel = input("Введите канал СберЧата (например, #tech-support): ")
                self.sberchat.ask_for_help(
                    result.get('query', 'Неизвестно'),
                    result.get('pages', [])
                )
                print("✅ Вопрос отправлен в СберЧат!")
