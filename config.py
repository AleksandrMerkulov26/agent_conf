# config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    # ---------- CONFLUENCE ----------
    confluence_url: str
    confluence_token: str
    confluence_email: str = ""
    
    # ---------- GIGACHAT ----------
    gigachat_url: str
    gigachat_token: str
    gigachat_auth_id: str = ""
    
    # ---------- СБЕРЧАТ ----------
    sberchat_webhook_url: str = ""  # Webhook URL для бота
    sberchat_bot_token: str = ""    # Токен бота (если используется)
    sberchat_chat_id: str = ""      # ID чата по умолчанию
    
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
    auto_sberchat_ask: bool = True  # Вместо auto_slack_ask
    
    @classmethod
    def from_env(cls):
        load_dotenv()
        
        return cls(
            confluence_url=os.getenv("CONFLUENCE_URL", ""),
            confluence_token=os.getenv("CONFLUENCE_TOKEN", ""),
            confluence_email=os.getenv("CONFLUENCE_EMAIL", ""),
            
            gigachat_url=os.getenv("GIGACHAT_URL", ""),
            gigachat_token=os.getenv("GIGACHAT_TOKEN", ""),
            gigachat_auth_id=os.getenv("GIGACHAT_AUTH_ID", ""),
            
            # СберЧат
            sberchat_webhook_url=os.getenv("SBERCHAT_WEBHOOK_URL", ""),
            sberchat_bot_token=os.getenv("SBERCHAT_BOT_TOKEN", ""),
            sberchat_chat_id=os.getenv("SBERCHAT_CHAT_ID", ""),
            
            cache_days=int(os.getenv("CACHE_DAYS", "30")),
            cache_file=os.getenv("CACHE_FILE", "owner_cache.json"),
            max_pages_to_analyze=int(os.getenv("MAX_PAGES_TO_ANALYZE", "5")),
            max_content_length=int(os.getenv("MAX_CONTENT_LENGTH", "5000")),
            follow_links_depth=int(os.getenv("FOLLOW_LINKS_DEPTH", "1")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "agent.log"),
            silent_mode=os.getenv("SILENT_MODE", "false").lower() == "true",
            auto_sberchat_ask=os.getenv("AUTO_SBERCHAT_ASK", "true").lower() == "true",
        )
    
    def validate(self):
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
