import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import numpy as np

class ChromaDBManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

    def create_collection(self, collection_name: str):
        return self.client.create_collection(name=collection_name)

    def get_or_create_collection(self, collection_name: str):
        try:
            return self.client.get_collection(name=collection_name)
        except ValueError:
            return self.create_collection(collection_name)

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def add_embeddings(self, collection_name: str, embeddings: List[List[float]], documents: Optional[List[str]], metadatas: List[Dict[str, Any]], ids: List[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

    def query_by_embeddings(self, collection_name: str, query_embeddings: List[List[float]], n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )

    def get_embeddings(self, collection_name: str, ids: List[str]) -> List[List[float]]:
        collection = self.get_or_create_collection(collection_name)
        result = collection.get(ids=ids, include=['embeddings'])
        return result['embeddings']

    def update_embeddings(self, collection_name: str, ids: List[str], embeddings: List[List[float]], documents: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None):
        collection = self.get_or_create_collection(collection_name)
        collection.update(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def delete_embeddings(self, collection_name: str, ids: List[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)

    def get_latest_document_id(self, collection_name: str) -> Optional[str]:
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=[[0] * 384],  # Dummy embedding
            n_results=1,
            include=['metadatas']
        )
        if results['ids'][0]:
            return max(results['ids'][0])
        return None
