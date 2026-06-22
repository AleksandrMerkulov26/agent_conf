# sberchat_notifier.py
import requests
import json
from typing import Optional, Dict, Any
from config import Config

class SberChatNotifier:
    """
    Отправляет уведомления в СберЧат (корпоративный мессенджер)
    Поддерживает webhook-уведомления и ботов
    """
    
    def __init__(self, config: Config):
        """
        Args:
            config: Объект с настройками, содержащий SBERCHAT_WEBHOOK_URL
        """
        self.webhook_url = config.sberchat_webhook_url
        self.bot_token = config.sberchat_bot_token if hasattr(config, 'sberchat_bot_token') else None
        self.chat_id = config.sberchat_chat_id if hasattr(config, 'sberchat_chat_id') else None
        
    def send_message(self, message: str, chat_id: Optional[str] = None) -> bool:
        """
        Отправляет текстовое сообщение в СберЧат
        
        Args:
            message: Текст сообщения
            chat_id: ID чата (если не указан, используется из конфига)
        
        Returns:
            True если отправлено успешно, иначе False
        """
        if not self.webhook_url:
            print("⚠️ SBERCHAT_WEBHOOK_URL не настроен. Сообщение не отправлено.")
            return False
        
        payload = {
            "text": message,
            "chat_id": chat_id or self.chat_id
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️ Ошибка отправки в СберЧат: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"⚠️ Исключение при отправке в СберЧат: {e}")
            return False
    
    def send_question(self, team_channel: str, question: str, context: str) -> bool:
        """
        Отправляет вопрос в канал команды в СберЧате
        
        Args:
            team_channel: Название канала (например, #payments-team)
            question: Вопрос, который нужно задать
            context: Контекст (логи, URL, найденные страницы)
        
        Returns:
            True если отправлено успешно, иначе False
        """
        message = f"""🤖 *Агент-помощник* задает вопрос:

**{question}**

📋 *Контекст:*
{context}

---
👥 Кто владеет этим сервисом? Ответьте в этом чате."""
        
        # Если team_channel начинается с #, убираем для API
        chat_id = team_channel.lstrip('#')
        return self.send_message(message, chat_id)
    
    def send_report(self, owner_info: Dict[str, Any]) -> bool:
        """
        Отправляет отчет о найденном владельце в СберЧат
        
        Args:
            owner_info: Словарь с информацией о владельце
                (team_name, contact, main_page_url, etc.)
        
        Returns:
            True если отправлено успешно, иначе False
        """
        if not owner_info.get("found"):
            message = f"""❌ *Владелец не найден*

🔍 Запрос: {owner_info.get('query', 'Неизвестно')}
📚 Найдено страниц: {owner_info.get('pages_found', 0)}

Попробуйте уточнить запрос или обратитесь в техподдержку."""
            return self.send_message(message)
        
        message = f"""✅ *Найден владелец сервиса!*

👤 *Команда-владелец:* {owner_info.get('team_name', 'Не указано')}
📧 *Контакт:* {owner_info.get('contact', 'Не указан')}
💬 *СберЧат:* {owner_info.get('slack', 'Не указан')}  # в вашем случае это может быть канал в СберЧате
📄 *Страница в Confluence:* {owner_info.get('main_page_url', 'Не найдена')}
📊 *Уверенность:* {owner_info.get('confidence', 'Не указана')}

---
📚 Найдено страниц: {owner_info.get('pages_found', 0)}
🔗 Ссылки на страницы:
"""
        
        # Добавляем список страниц
        for page in owner_info.get("pages", [])[:5]:
            message += f"\n• {page.get('title')}: {page.get('url')}"
        
        if owner_info.get("from_cache"):
            message += "\n\n📦 *Результат взят из кеша* (быстрый ответ)"
        
        return self.send_message(message)
    
    def ask_for_help(self, query: str, pages: list) -> bool:
        """
        Отправляет запрос о помощи, если владелец не найден
        
        Args:
            query: Исходный запрос пользователя
            pages: Найденные страницы (для контекста)
        
        Returns:
            True если отправлено успешно, иначе False
        """
        pages_text = "\n".join([f"• {p['title']}: {p['url']}" for p in pages[:3]])
        
        message = f"""🆘 *Требуется помощь в поиске владельца!*

🔍 *Запрос:* {query}

📚 *Найдены страницы в Confluence (возможно, связаны):*
{pages_text}

---
Просьба к командам: кто владеет этим сервисом? Напишите в чат."""
        
        return self.send_message(message)
