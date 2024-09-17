from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from personal_ai_assistant.web.scraper import WebScraper
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


def get_web_scraper():
    return WebScraper()


@router.get("/scrape")
async def scrape_url(
    url: str,
    token: str = Depends(oauth2_scheme),
    web_scraper: WebScraper = Depends(get_web_scraper)
):
    try:
        scraped_data = await web_scraper.scrape_url(url)
        logger.info(f"Successfully scraped data from URL: {url}")
        return {"scraped_data": scraped_data}
    except Exception as e:
        logger.error(f"Error scraping URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scraping URL")
