import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from personal_ai_assistant.llm.text_processor import TextProcessor


class WebScraper:
    def __init__(self, text_processor: Optional[TextProcessor] = None):
        self.text_processor = text_processor

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string if soup.title else ""
                    content = ""
                    for paragraph in soup.find_all('p'):
                        content += paragraph.text + "\n"
                    author = soup.find('meta', {'name': 'author'})
                    author = author['content'] if author else "Unknown"
                    date = soup.find('meta', {'name': 'date'})
                    date = date['content'] if date else "Unknown"
                    return {
                        "title": title,
                        "content": content,
                        "author": author,
                        "date": date,
                        "url": url
                    }
                else:
                    return {"error": f"Failed to fetch URL. Status code: {response.status}"}

    async def summarize_content(self, content: str, max_length: int = 200) -> str:
        if self.text_processor:
            return await self.text_processor.summarize_text(content, max_length)
        else:
            # Simple summarization if text_processor is not available
            words = content.split()
            return " ".join(words[:max_length]) + \
                ("..." if len(words) > max_length else "")
