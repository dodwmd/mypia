import pytest
from unittest.mock import patch, MagicMock
from personal_ai_assistant.vector_db.chroma_db import ChromaDBManager


@pytest.fixture
def chroma_db_manager():
    with patch('personal_ai_assistant.vector_db.chroma_db.chromadb.Client') as mock_client:
        mock_client.return_value = MagicMock()
        return ChromaDBManager()


def test_create_collection(chroma_db_manager):
    chroma_db_manager.client.create_collection.return_value = MagicMock()

    result = chroma_db_manager.create_collection("test_collection")

    assert result is not None
    chroma_db_manager.client.create_collection.assert_called_once_with(name="test_collection")


def test_add_documents(chroma_db_manager):
    mock_collection = MagicMock()
    chroma_db_manager.get_or_create_collection = MagicMock(return_value=mock_collection)

    chroma_db_manager.add_documents("test_collection", ["doc1", "doc2"], [
                                    {"meta": "data1"}, {"meta": "data2"}], ["id1", "id2"])

    mock_collection.add.assert_called_once_with(
        documents=["doc1", "doc2"],
        metadatas=[{"meta": "data1"}, {"meta": "data2"}],
        ids=["id1", "id2"]
    )


def test_query(chroma_db_manager):
    mock_collection = MagicMock()
    chroma_db_manager.get_or_create_collection = MagicMock(return_value=mock_collection)
    mock_collection.query.return_value = {"results": ["result1", "result2"]}

    result = chroma_db_manager.query("test_collection", ["query_text"], n_results=2)

    assert result == {"results": ["result1", "result2"]}
    mock_collection.query.assert_called_once_with(
        query_texts=["query_text"],
        n_results=2
    )
