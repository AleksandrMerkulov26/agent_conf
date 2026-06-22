import requests

class ConfluenceClient:
    def __init__(self):
        self.base_url = "https://confluence.company.com/rest/api"
        self.token = "ВАШ_ТОКЕН_ДОСТУПА"
    
    def search(self, query):
        # Запрос к Confluence API
        url = f"{self.base_url}/search"
        params = {"cql": f'text~"{query}"'}  # Ищем текст
        response = requests.get(url, params=params, auth=(self.token, ""))
        
        pages = []
        for result in response.json()["results"]:
            pages.append({
                "title": result["title"],
                "url": result["url"],
                "id": result["id"]
            })
        return pages
