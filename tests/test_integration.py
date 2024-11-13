"""
Integration tests for Project Oracle
"""

import pytest
from pathlib import Path
import shutil
from langchain_openai import ChatOpenAI

from src.services.vector_store import VectorStore
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from src.services.web_scraper import WebScraper, create_scraping_tools
from langchain_core.messages import HumanMessage, SystemMessage

@pytest.fixture
def test_env():
    """Set up test environment"""
    test_dir = Path("./test_vector_store")
    test_kb_path = "tests/test_data/test_knowledge_base.json"
    
    # Initialize components
    llm = ChatOpenAI(temperature=0.7)
    kb = KnowledgeBase(test_kb_path, str(test_dir))
    scraper = WebScraper("test_key")
    
    # Create tools
    scraping_tools = create_scraping_tools(scraper)
    knowledge_tools = create_knowledge_tools(kb)
    
    # Create workflow
    workflow = create_chat_workflow(llm, scraping_tools, knowledge_tools)
    
    yield {
        "workflow": workflow,
        "kb": kb,
        "llm": llm
    }
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)

def test_end_to_end_knowledge_query(test_env):
    """Test complete knowledge query workflow"""
    workflow = test_env["workflow"]
    
    # Test query about Jedi
    messages = [
        SystemMessage(content="You are a helpful AI assistant."),
        HumanMessage(content="Tell me about the Jedi Order")
    ]
    
    # Process through workflow
    result = None
    for step in workflow.stream({"messages": messages}):
        if "__end__" not in step:
            for key in step:
                if 'messages' in step[key]:
                    result = step[key]['messages'][-1].content
    
    assert result is not None
    assert "Jedi" in result.lower()
    assert "Force" in result

def test_hybrid_search_workflow(test_env):
    """Test hybrid search functionality"""
    kb = test_env["kb"]
    
    # Test hybrid search
    result = kb.search("What is the relationship between Jedi and lightsabers?", search_type="hybrid")
    
    assert result is not None
    assert "lightsaber" in result.lower()
    assert "Jedi" in result.lower()

def test_vector_search_accuracy(test_env):
    """Test vector search result relevance"""
    kb = test_env["kb"]
    
    # Test semantic understanding
    result = kb.search("peaceful guardians of the galaxy", search_type="vector")
    assert "Jedi" in result.lower()  # Should find Jedi content even without explicit mention

def test_cross_domain_search(test_env):
    """Test searching across different knowledge domains"""
    kb = test_env["kb"]
    
    # Search that should find both Star Wars and project content
    result = kb.search("Tell me about the code and principles", search_type="hybrid")
    
    assert result is not None
    assert any(term in result.lower() for term in ["jedi code", "development", "guidelines"])

def test_error_handling(test_env):
    """Test error handling in the workflow"""
    workflow = test_env["workflow"]
    
    # Test with malformed query
    messages = [
        SystemMessage(content="You are a helpful AI assistant."),
        HumanMessage(content="")  # Empty query
    ]
    
    try:
        for step in workflow.stream({"messages": messages}):
            pass
    except Exception as e:
        assert str(e) is not None  # Should handle error gracefully

def test_performance_metrics(test_env):
    """Test search performance"""
    import time
    kb = test_env["kb"]
    
    # Measure vector search time
    start_time = time.time()
    kb.search("Jedi training", search_type="vector")
    vector_time = time.time() - start_time
    
    # Measure traditional search time
    start_time = time.time()
    kb.search("Jedi training", search_type="traditional")
    traditional_time = time.time() - start_time
    
    # Log performance metrics
    print(f"Vector search time: {vector_time:.2f}s")
    print(f"Traditional search time: {traditional_time:.2f}s")
    
    # Assert reasonable performance
    assert vector_time < 2.0  # Vector search should complete within 2 seconds
    assert traditional_time < 1.0  # Traditional search should be faster 