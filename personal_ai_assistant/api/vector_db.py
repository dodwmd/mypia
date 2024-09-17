from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import logging

from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


class VectorDBDocument(BaseModel):
    collection_name: str
    document: str
    metadata: Optional[dict] = None


class VectorDBQuery(BaseModel):
    collection_name: str
    query_text: str
    n_results: int = 5


def get_chroma_db():
    return ChromaDBManager(settings.chroma_db_path)


@router.post("/add")
async def add_to_vectordb(
    document: VectorDBDocument,
    token: str = Depends(oauth2_scheme),
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    try:
        await chroma_db.add_documents(document.collection_name, [document.document], [document.metadata])
        logger.info(f"Successfully added document to vector database collection: {document.collection_name}")
        return {"message": "Document added successfully"}
    except Exception as e:
        logger.error(f"Error adding document to vector database: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding document to vector database")


@router.post("/query")
async def query_vectordb(
    query: VectorDBQuery,
    token: str = Depends(oauth2_scheme),
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    try:
        results = await chroma_db.query(query.collection_name, [query.query_text], query.n_results)
        logger.info(f"Successfully queried vector database collection: {query.collection_name}")
        return {"results": results}
    except Exception as e:
        logger.error(f"Error querying vector database: {str(e)}")
        raise HTTPException(status_code=500, detail="Error querying vector database")
