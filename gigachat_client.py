import requests

class GigaChatClient:
    def __init__(self):
        self.api_url = "https://gigachat.company.com/api/v1/chat"
        self.token = "ВАШ_ТОКЕН"
    
    def find_owner(self, search_text, pages):
        # Собираем текст для нейросети
        prompt = f"""
        Я ищу владельца системы или сервиса по запросу: "{search_text}"
        
        Вот несколько страниц из Confluence, которые могут быть связаны:
        """
        
        for i, page in enumerate(pages, 1):
            prompt += f"""
            --- Страница {i}: {page['title']} ---
            URL: {page['url']}
            Содержание:
            {page['content']}
            ---
            """
        
        prompt += """
        Проанализируй эти страницы и ответь строго в JSON формате:
        {
            "main_page_url": "ссылка на самую релевантную страницу",
            "team_name": "название команды-владельца",
            "contact": "имя или почта контактного лица",
            "slack": "название Slack канала (если есть)",
            "confidence": "низкая/средняя/высокая уверенность"
        }
        
        Если на страницах нет информации о владельце, то в поле team_name напиши "НЕ НАЙДЕНО".
        """
        
        # Отправляем запрос к GigaChat
        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.token}"},
            json={"messages": [{"role": "user", "content": prompt}]}
        )
        
        # Представим, что нейросеть вернула JSON
        return response.json()
