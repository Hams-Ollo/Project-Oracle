"""
Performance tests for Project Oracle
"""

import pytest
import time
from pathlib import Path
import shutil
from statistics import mean, stdev
from typing import List, Dict

from src.services.vector_store import VectorStore
from src.services.knowledge_base import KnowledgeBase
from src.core.workflow import create_chat_workflow
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

@pytest.fixture
def performance_env():
    """Set up performance testing environment"""
    test_dir = Path("./test_vector_store")
    test_kb_path = "tests/test_data/test_knowledge_base.json"
    
    # Initialize components
    llm = ChatOpenAI(temperature=0.7)
    kb = KnowledgeBase(test_kb_path, str(test_dir))
    
    yield {
        "kb": kb,
        "vector_store": kb.vector_store,
        "llm": llm
    }
    
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)

def measure_search_time(func, query: str, iterations: int = 5) -> Dict[str, float]:
    """Measure search execution time"""
    times = []
    for _ in range(iterations):
        start_time = time.time()
        func(query)
        times.append(time.time() - start_time)
    
    return {
        "mean": mean(times),
        "std_dev": stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times)
    }

def test_vector_search_performance(performance_env):
    """Test vector search performance"""
    kb = performance_env["kb"]
    
    # Test queries
    queries = [
        "Tell me about the Jedi Order",
        "What is the Rule of Two?",
        "How are lightsabers constructed?",
        "Explain Mandalorian culture",
        "What is Project Oracle's architecture?"
    ]
    
    # Measure vector search performance
    vector_times = []
    for query in queries:
        metrics = measure_search_time(
            lambda q: kb.search(q, search_type="vector"),
            query
        )
        vector_times.append(metrics)
        print(f"\nVector Search - Query: {query}")
        print(f"Mean time: {metrics['mean']:.3f}s")
        print(f"Std Dev: {metrics['std_dev']:.3f}s")
    
    # Assert performance requirements
    for metrics in vector_times:
        assert metrics["mean"] < 2.0, "Vector search too slow"
        assert metrics["std_dev"] < 0.5, "Vector search time too variable"

def test_hybrid_search_performance(performance_env):
    """Test hybrid search performance"""
    kb = performance_env["kb"]
    
    # Complex queries requiring hybrid search
    queries = [
        "Compare Jedi and Sith philosophies",
        "Explain the relationship between Mandalorians and the Force",
        "How does Project Oracle handle different types of queries?",
        "What are the similarities between Jedi training and developer onboarding?",
        "Describe the impact of Order 66 on the galaxy"
    ]
    
    # Measure hybrid search performance
    hybrid_times = []
    for query in queries:
        metrics = measure_search_time(
            lambda q: kb.search(q, search_type="hybrid"),
            query
        )
        hybrid_times.append(metrics)
        print(f"\nHybrid Search - Query: {query}")
        print(f"Mean time: {metrics['mean']:.3f}s")
        print(f"Std Dev: {metrics['std_dev']:.3f}s")
    
    # Assert performance requirements
    for metrics in hybrid_times:
        assert metrics["mean"] < 3.0, "Hybrid search too slow"
        assert metrics["std_dev"] < 0.75, "Hybrid search time too variable"

def test_concurrent_search_performance(performance_env):
    """Test performance under concurrent searches"""
    import concurrent.futures
    kb = performance_env["kb"]
    
    queries = [
        "Jedi Order",
        "Sith Empire",
        "Mandalorians",
        "Project Setup",
        "Development Guide"
    ] * 2  # Run each query twice
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(kb.search, query, "vector")
            for query in queries
        ]
        results = [f.result() for f in futures]
    
    total_time = time.time() - start_time
    
    # Assert concurrent performance requirements
    assert total_time < len(queries) * 2.0, "Concurrent search performance inadequate"
    assert all(isinstance(r, str) for r in results), "Some searches failed"

def test_memory_usage(performance_env):
    """Test memory usage during search operations"""
    import psutil
    import os
    
    kb = performance_env["kb"]
    process = psutil.Process(os.getpid())
    
    # Measure baseline memory
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Perform multiple searches
    for _ in range(10):
        kb.search("Jedi Order", search_type="vector")
        kb.search("Project Setup", search_type="hybrid")
    
    # Measure memory after searches
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - baseline_memory
    
    print(f"\nMemory Usage:")
    print(f"Baseline: {baseline_memory:.2f}MB")
    print(f"Final: {final_memory:.2f}MB")
    print(f"Increase: {memory_increase:.2f}MB")
    
    # Assert memory usage requirements
    assert memory_increase < 500, "Excessive memory usage" 