import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import logging
from personal_ai_assistant.config import settings

logger = logging.getLogger(__name__)

class ChromaDBManager:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.chroma_db_host,
            port=settings.chroma_db_port,
        )
        logger.info(f"ChromaDB initialized with host: {settings.chroma_db_host}, port: {settings.chroma_db_port}")

    def create_collection(self, collection_name: str):
        return self.client.create_collection(name=collection_name)

    def get_or_create_collection(self, collection_name: str):
        try:
            return self.client.get_collection(name=collection_name)
        except ValueError:
            return self.client.create_collection(name=collection_name)

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        collection = self.get_or_create_collection(collection_name)
        logger.info(f"Adding {len(documents)} documents to collection: {collection_name}")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Added {len(documents)} documents to collection: {collection_name}")

    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        logger.info(f"Querying collection: {collection_name}")
        logger.debug(f"Query texts: {query_texts}")
        logger.debug(f"Number of results requested: {n_results}")
        results = collection.query(
            query_texts=query_texts,
            n_results=n_results
        )
        logger.info(f"Query returned {len(results['documents'])} results")
        logger.debug(f"Query results: {results}")
        return results

    def get_document(self, collection_name: str, document_id: str):
        collection = self.get_or_create_collection(collection_name)
        return collection.get(ids=[document_id])

    def update_document(self, collection_name: str, document_id: str, document: str, metadata: Dict[str, Any]):
        collection = self.get_or_create_collection(collection_name)
        collection.update(
            ids=[document_id],
            documents=[document],
            metadatas=[metadata]
        )

    def delete_document(self, collection_name: str, document_id: str):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=[document_id])

    def list_collections(self):
        return self.client.list_collections()

    def get_collection(self, collection_name: str):
        return self.client.get_collection(name=collection_name)

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(name=collection_name)

    def get_latest_document_id(self, collection_name: str) -> str:
        collection = self.get_or_create_collection(collection_name)
        # Assuming the IDs are sortable and the latest one is the highest
        results = collection.get(limit=1, sort="id", order="desc")
        return results['ids'][0] if results['ids'] else None

    def delete_documents(self, collection_name: str, filter: Dict[str, Any] = None):
        collection = self.get_or_create_collection(collection_name)
        if filter:
            # Assuming the filter is in the format that Chroma expects
            collection.delete(where=filter)
        else:
            # If no filter is provided, delete all documents
            collection.delete()

    def get_collection_stats(self, collection_name: str):
        collection = self.get_or_create_collection(collection_name)
        return {
            "total_documents": collection.count(),
            "embedding_dimension": getattr(collection, 'dimension', 'Unknown'),
        }
