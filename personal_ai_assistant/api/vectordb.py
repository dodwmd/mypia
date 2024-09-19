from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
import logging
import traceback
import sys
import io
from PyPDF2 import PdfReader

from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class VectorDBDocument(BaseModel):
    collection_name: str
    document: str
    metadata: Optional[dict] = None

class VectorDBQuery(BaseModel):
    collection_name: str
    query_text: str
    n_results: int = 5

def get_chroma_db():
    return ChromaDBManager()

@router.post("/upload")
async def upload_to_vectordb(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    logger.debug("Entering upload_to_vectordb route")
    try:
        logger.info(f"Received file upload request: {file.filename}")
        logger.debug(f"Token: {token[:10]}...")  # Log part of the token for debugging
        
        contents = await file.read()
        logger.info(f"File contents read, size: {len(contents)} bytes")

        collection_name = "default_collection"
        
        logger.info(f"Attempting to add document to collection: {collection_name}")
        logger.debug(f"ChromaDBManager instance: {chroma_db}")
        logger.debug(f"Collection name: {collection_name}")
        
        # Extract text from PDF
        pdf_reader = PdfReader(io.BytesIO(contents))
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        logger.debug(f"Extracted text content (first 100 chars): {text_content[:100]}")
        
        metadata = {"filename": file.filename}
        
        logger.info("Calling add_documents method...")
        chroma_db.add_documents(collection_name, [text_content], [metadata], [file.filename])
        
        logger.info(f"Successfully added document to vector database collection: {collection_name}")
        return {"message": "Document added successfully"}
    except Exception as e:
        error_msg = f"Error in upload_to_vectordb: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/query")
async def query_vectordb(
    query: VectorDBQuery,
    chroma_db: ChromaDBManager = Depends(get_chroma_db)
):
    logger.debug("Entering query_vectordb route")
    try:
        logger.info(f"Received query request for collection: {query.collection_name}")
        logger.debug(f"Query text: {query.query_text}")
        logger.debug(f"Number of results requested: {query.n_results}")
        
        logger.debug(f"ChromaDBManager instance: {chroma_db}")
        
        # Log available collections
        try:
            collections = chroma_db.list_collections()
            logger.debug(f"Available collections: {collections}")
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            collections = []
        
        try:
            collection = chroma_db.get_or_create_collection(query.collection_name)
        except Exception as e:
            logger.error(f"Error getting or creating collection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error accessing collection: {str(e)}")
        
        logger.info(f"Querying collection: {query.collection_name}")
        results = chroma_db.query(query.collection_name, [query.query_text], query.n_results)
        
        logger.debug(f"Query results: {results}")
        logger.info(f"Query returned {len(results['documents'][0]) if results['documents'] else 0} results")
        
        # Add some stats to the response
        try:
            collection_stats = chroma_db.get_collection_stats(query.collection_name)
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            collection_stats = {"error": str(e)}
        
        return {
            "results": results,
            "stats": collection_stats
        }
    except HTTPException as he:
        logger.error(f"HTTP exception in query_vectordb: {str(he)}")
        raise he
    except Exception as e:
        error_msg = f"Error in query_vectordb: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)
