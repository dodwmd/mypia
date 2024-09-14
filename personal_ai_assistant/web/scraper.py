import trafilatura
from typing import Optional, Dict, List
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from personal_ai_assistant.llm.text_processor import TextProcessor

class WebScraper:
    @staticmethod
    def scrape_url(url: str) -> Optional[Dict[str, str]]:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return None

        result = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        if result is None:
            return None

        metadata = trafilatura.extract_metadata(downloaded)

        return {
            'url': url,
            'title': metadata.title if metadata else '',
            'author': metadata.author if metadata else '',
            'date': metadata.date if metadata else '',
            'content': result
        }

    @staticmethod
    def extract_links(url: str) -> List[str]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
        links = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if href.startswith('/'):
                    links.append(base_url + href)
                elif href.startswith('http'):
                    links.append(href)
        return links

class WebContentProcessor:
    def __init__(self, text_processor: TextProcessor):
        self.text_processor = text_processor

    def process_url(self, url: str) -> Dict[str, Any]:
        scraped_data = WebScraper.scrape_url(url)
        if not scraped_data:
            return {"status": "error", "message": f"Failed to scrape content from {url}"}

        summary = self.text_processor.summarize_text(scraped_data['content'], max_length=200)
        keywords = self.extract_keywords(scraped_data['content'])
        sentiment = self.analyze_sentiment(scraped_data['content'])
        
        return {
            "status": "success",
            "url": url,
            "title": scraped_data['title'],
            "author": scraped_data['author'],
            "date": scraped_data['date'],
            "summary": summary,
            "keywords": keywords,
            "sentiment": sentiment
        }

    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        prompt = f"Extract {num_keywords} key words or phrases from the following text:\n\n{text}\n\nKeywords:"
        response = self.text_processor.generate_text(prompt, max_tokens=50)
        return [keyword.strip() for keyword in response.split(',')]

    def analyze_sentiment(self, text: str) -> str:
        prompt = f"Analyze the sentiment of the following text and categorize it as positive, negative, or neutral:\n\n{text}\n\nSentiment:"
        return self.text_processor.generate_text(prompt, max_tokens=10).strip()

    def compare_urls(self, url1: str, url2: str) -> Dict[str, Any]:
        data1 = self.process_url(url1)
        data2 = self.process_url(url2)

        if data1["status"] == "error" or data2["status"] == "error":
            return {"status": "error", "message": "Failed to process one or both URLs"}

        comparison = self.text_processor.generate_text(
            f"Compare and contrast the following two web pages:\n\n"
            f"Page 1: {data1['title']}\nSummary: {data1['summary']}\n\n"
            f"Page 2: {data2['title']}\nSummary: {data2['summary']}\n\n"
            f"Provide a brief comparison:"
        )

        return {
            "status": "success",
            "url1": data1,
            "url2": data2,
            "comparison": comparison
        }

    def analyze_topic(self, topic: str, num_urls: int = 3) -> Dict[str, Any]:
        search_url = f"https://www.google.com/search?q={topic.replace(' ', '+')}"
        links = WebScraper.extract_links(search_url)[:num_urls]

        results = []
        for url in links:
            results.append(self.process_url(url))

        analysis = self.text_processor.generate_text(
            f"Analyze the following information about the topic '{topic}':\n\n" +
            "\n\n".join([f"Source: {r['url']}\nSummary: {r['summary']}" for r in results if r['status'] == 'success']) +
            f"\n\nProvide a comprehensive analysis of the topic '{topic}' based on these sources:"
        )

        return {
            "status": "success",
            "topic": topic,
            "sources": results,
            "analysis": analysis
        }
