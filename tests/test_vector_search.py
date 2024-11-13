"""
Tests for vector search functionality
"""

import pytest
from pathlib import Path
import shutil
from src.services.vector_store import VectorStore
from src.services.knowledge_base import KnowledgeBase
from langchain.schema import Document

@pytest.fixture
def test_vector_store():
    """Create a test vector store"""
    test_dir = Path("./test_vector_store")
    vector_store = VectorStore(str(test_dir))
    yield vector_store
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)

@pytest.fixture
def test_knowledge_base():
    """Create a test knowledge base"""
    kb = KnowledgeBase("tests/test_data/test_knowledge_base.json")
    return kb

def test_vector_store_initialization(test_vector_store):
    """Test vector store initialization"""
    assert test_vector_store.store is not None
    assert test_vector_store.persist_dir.exists()

def test_document_processing(test_vector_store):
    """Test JSON to document conversion"""
    test_data = {
        "topics": {
            "test_topic": {
                "definition": "Test definition",
                "key_concepts": ["concept1", "concept2"]
            }
        }
    }
    
    documents = test_vector_store.process_json_data(test_data)
    assert len(documents) > 0
    assert isinstance(documents[0], Document)
    assert "Test definition" in documents[0].page_content

def test_vector_search(test_knowledge_base):
    """Test vector similarity search"""
    # Test with Star Wars related query
    results = test_knowledge_base.search("Tell me about Jedi training", search_type="vector")
    assert results is not None
    assert "Jedi" in results.lower()
    
    # Test with technical documentation query
    results = test_knowledge_base.search("How to set up the project", search_type="vector")
    assert results is not None
    assert "setup" in results.lower() or "installation" in results.lower()

def test_hybrid_search(test_knowledge_base):
    """Test hybrid search functionality"""
    results = test_knowledge_base.search("What is the Rule of Two", search_type="hybrid")
    assert results is not None
    assert "sith" in results.lower()
    assert "rule of two" in results.lower()

def test_search_performance(test_knowledge_base):
    """Test search response times"""
    import time
    
    start_time = time.time()
    test_knowledge_base.search("Jedi Order", search_type="vector")
    vector_time = time.time() - start_time
    
    start_time = time.time()
    test_knowledge_base.search("Jedi Order", search_type="traditional")
    traditional_time = time.time() - start_time
    
    # Log performance metrics
    print(f"Vector search time: {vector_time:.2f}s")
    print(f"Traditional search time: {traditional_time:.2f}s")
    
    # Ensure reasonable response times
    assert vector_time < 2.0  # Vector search should complete within 2 seconds
    assert traditional_time < 1.0  # Traditional search should be faster 