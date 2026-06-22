import json
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_file="owner_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get_owner(self, query):
        """Если мы уже искали такой запрос, возвращаем сохраненный ответ"""
        # Нормализуем запрос (убираем лишние пробелы, приводим к нижнему регистру)
        key = query.lower().strip()
        
        if key in self.cache:
            cached = self.cache[key]
            # Если кешу меньше 30 дней, считаем его актуальным
            if datetime.now() - datetime.fromisoformat(cached["timestamp"]) < timedelta(days=30):
                return cached["result"]
        return None
    
    def save_owner(self, query, result):
        """Сохраняем найденный ответ"""
        key = query.lower().strip()
        self.cache[key] = {
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        self._save_cache()
