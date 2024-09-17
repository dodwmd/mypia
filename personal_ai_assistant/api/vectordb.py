from fastapi import APIRouter, UploadFile, File, Depends
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager
from personal_ai_assistant.api.dependencies import get_chroma_db

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), chroma_db: ChromaDBManager = Depends(get_chroma_db)):
    contents = await file.read()
    # Process the file contents and add to the vector database
    # This is a placeholder implementation. You'll need to adapt this to your specific needs.
    chroma_db.add_document(file.filename, contents.decode())
    return {"message": "File uploaded and processed successfully"}

@router.post("/query")
async def query_vectordb(query: str, chroma_db: ChromaDBManager = Depends(get_chroma_db)):
    results = chroma_db.query(query)
    return {"results": results}
