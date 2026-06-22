class EntityResolver:
    def __init__(self):
        self.servicies = {
            "payment": ["платеж", "pay", "транзакция"],
            "auth": ["авторизация", "логин", "token", "jwt"],
            "database": ["база", "sql", "postgres", "db"]
        }
    
    def extract_keywords(self, user_input):
        """Извлекает ключевые слова из запроса"""
        # Убираем мусор из логов
        clean_text = user_input.lower()
        
        # Удаляем временные метки, IP-адреса и т.д.
        # Например, превращаем "ERROR 2024-01-15 10:30:25 [payments] timeout" -> "payments timeout"
        
        keywords = []
        
        # Ищем известные сервисы
        for service, synonyms in self.servicies.items():
            if any(syn in clean_text for syn in synonyms):
                keywords.append(service)
        
        # Извлекаем все слова, похожие на названия сервисов (с большой буквы, с суффиксом -service и т.д.)
        # Например: "PaymentService", "auth-api" -> ["PaymentService", "auth-api"]
        
        # Ищем URL и извлекаем из них домен
        # "https://api.payments.internal/v2/status" -> "payments"
        
        return keywords
