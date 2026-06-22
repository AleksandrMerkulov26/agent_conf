from bs4 import BeautifulSoup

class LinkFollower:
    def __init__(self, confluence_client):
        self.confluence = confluence_client
    
    def follow_links(self, page_id, search_terms, depth=1):
        """Ищет информацию на странице и на связанных страницах"""
        visited = set()
        results = []
        
        def _search_page(page_id, current_depth):
            if page_id in visited or current_depth > depth:
                return
            
            visited.add(page_id)
            content = self.confluence.get_page_content(page_id)
            
            # Ищем на странице нужные термины
            if any(term in content.lower() for term in search_terms):
                results.append({
                    "page_id": page_id,
                    "url": self.confluence.get_page_url(page_id),
                    "found": True
                })
                return  # Если нашли, дальше не идем
            
            # Ищем ссылки на другие страницы
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if '/pages/' in href:  # Это ссылка на другую страницу Confluence
                    linked_page_id = extract_id_from_url(href)
                    if linked_page_id:
                        _search_page(linked_page_id, current_depth + 1)
        
        _search_page(page_id, 0)
        return results
