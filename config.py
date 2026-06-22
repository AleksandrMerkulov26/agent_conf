# config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    # ---------- CONFLUENCE ----------
    confluence_url: str
    confluence_token: str
    confluence_email: str = ""  # Опционально, для некоторых типов авторизации
    
    # ---------- GIGACHAT ----------
    gigachat_url: str
    gigachat_token: str
    gigachat_auth_id: str = ""  # Для OAuth2, если требуется
    
    # ---------- SLACK ----------
    slack_webhook_url: str = ""  # Опционально, если не используешь Slack
    
    # ---------- НАСТРОЙКИ КЕША ----------
    cache_days: int = 30
    cache_file: str = "owner_cache.json"
    
    # ---------- НАСТРОЙКИ ПОИСКА ----------
    max_pages_to_analyze: int = 5
    max_content_length: int = 5000
    follow_links_depth: int = 1
    
    # ---------- НАСТРОЙКИ ЛОГИРОВАНИЯ ----------
    log_level: str = "INFO"
    log_file: str = "agent.log"
    
    # ---------- РЕЖИМЫ РАБОТЫ ----------
    silent_mode: bool = False
    auto_slack_ask: bool = True
    
    @classmethod
    def from_env(cls):
        """Загружает настройки из переменных окружения"""
        load_dotenv()  # Загружаем .env файл
        
        return cls(
            # Confluence
            confluence_url=os.getenv("CONFLUENCE_URL", ""),
            confluence_token=os.getenv("CONFLUENCE_TOKEN", ""),
            confluence_email=os.getenv("CONFLUENCE_EMAIL", ""),
            
            # GigaChat
            gigachat_url=os.getenv("GIGACHAT_URL", ""),
            gigachat_token=os.getenv("GIGACHAT_TOKEN", ""),
            gigachat_auth_id=os.getenv("GIGACHAT_AUTH_ID", ""),
            
            # Slack
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
            
            # Настройки кеша (с преобразованием типов)
            cache_days=int(os.getenv("CACHE_DAYS", "30")),
            cache_file=os.getenv("CACHE_FILE", "owner_cache.json"),
            
            # Настройки поиска
            max_pages_to_analyze=int(os.getenv("MAX_PAGES_TO_ANALYZE", "5")),
            max_content_length=int(os.getenv("MAX_CONTENT_LENGTH", "5000")),
            follow_links_depth=int(os.getenv("FOLLOW_LINKS_DEPTH", "1")),
            
            # Настройки логирования
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "agent.log"),
            
            # Режимы работы (с преобразованием в bool)
            silent_mode=os.getenv("SILENT_MODE", "false").lower() == "true",
            auto_slack_ask=os.getenv("AUTO_SLACK_ASK", "true").lower() == "true",
        )
    
    def validate(self):
        """Проверяет, что все обязательные настройки заполнены"""
        required = [
            ("CONFLUENCE_URL", self.confluence_url),
            ("CONFLUENCE_TOKEN", self.confluence_token),
            ("GIGACHAT_URL", self.gigachat_url),
            ("GIGACHAT_TOKEN", self.gigachat_token),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(
                f"❌ Отсутствуют обязательные настройки: {', '.join(missing)}\n"
                "Пожалуйста, создай файл .env на основе .env.example"
            )
        
        return True
