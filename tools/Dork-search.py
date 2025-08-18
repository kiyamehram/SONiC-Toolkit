import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

class DorkSearch:
    def __init__(self, user_agent=None, delay=2):
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.delay = delay  
        self.session = requests.Session()
        
    def search(self, dork_query, pages=1):
        results = []
        
        for page in range(pages):
            start = page * 10
            url = self._build_search_url(dork_query, start)
            
            try:
                html = self._make_request(url)
                if html:
                    page_results = self._parse_results(html)
                    results.extend(page_results)
                
                time.sleep(self.delay + random.uniform(0, 1))
                
            except Exception as e:
                print(f"Error on page {page+1}: {e}")
                break
                
        return results
    
    def _build_search_url(self, query, start=0):
        base_url = "https://www.google.com/search"
        params = {
            "q": query,
            "start": start,
            "num": 10,  
            "filter": 0  
        }
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    
    def _make_request(self, url):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def _parse_results(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for result in soup.select('div.g'):
            try:
                link = result.select_one('a[href^="http"]')
                if not link:
                    continue
                    
                url = link['href']
                title = link.text.strip()
                
                snippet = ""
                snippet_element = result.select_one('.IsZvec, .VwiC3b')
                if snippet_element:
                    snippet = snippet_element.text.strip()
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue
                
        return results

def display_banner():
    banner = """
88888888ba,                          88                                                                 88           
88      `"8b                         88                                                                 88           
88        `8b                        88                                                                 88           
88         88  ,adPPYba,  8b,dPPYba, 88   ,d8     ,adPPYba,  ,adPPYba, ,adPPYYba, 8b,dPPYba,  ,adPPYba, 88,dPPYba,   
88         88 a8"     "8a 88P'   "Y8 88 ,a8"      I8[    "" a8P_____88 ""     `Y8 88P'   "Y8 a8"     "" 88P'    "8a  
88         8P 8b       d8 88         8888[         `"Y8ba,  8PP""""""" ,adPPPPP88 88         8b         88       88  
88      .a8P  "8a,   ,a8" 88         88`"Yba,     aa    ]8I "8b,   ,aa 88,    ,88 88         "8a,   ,aa 88       88  
88888888Y"'    `"YbbdP"'  88         88   `Y8a    `"YbbdP"'  `"Ybbd8"' `"8bbdP"Y8 88          `"Ybbd8"' 88       88
    """
    print(banner)

if __name__ == "__main__":
    display_banner()
    dork_search = DorkSearch()
    
    dorks = [
        'site:example.com filetype:pdf',
        'intitle:"index of" "parent directory"',
        'inurl:admin/login.php',
        'ext:sql intext:password'
    ]
    
    print("\n[+] Testing with sample dorks...\n")
    
    for dork in dorks:
        print(f"\n[+] Searching for: {dork}")
        results = dork_search.search(dork, pages=1)
        
        if not results:
            print("[-] No results found or request blocked by Google")
            continue
            
        for i, result in enumerate(results, 1):
            print(f"\n[+] Result {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet'][:100]}...")