from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from personal_ai_assistant.llm.text_processor import TextProcessor
import logging

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

def get_text_processor():
    return TextProcessor()

@router.post("/summarize")
async def summarize_text(
    text: str,
    max_length: int = 100,
    token: str = Depends(oauth2_scheme),
    text_processor: TextProcessor = Depends(get_text_processor)
):
    try:
        summary = await text_processor.summarize_text(text, max_length)
        logger.info(f"Successfully summarized text of length {len(text)}")
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error summarizing text")

@router.post("/generate")
async def generate_text(
    prompt: str,
    max_length: int = 100,
    token: str = Depends(oauth2_scheme),
    text_processor: TextProcessor = Depends(get_text_processor)
):
    try:
        generated_text = await text_processor.generate_text(prompt, max_length)
        logger.info(f"Successfully generated text from prompt of length {len(prompt)}")
        return {"generated_text": generated_text}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating text")
