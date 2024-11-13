"""
Knowledge base service for information storage and retrieval.
"""

import json
from typing import List, Optional
from pathlib import Path
from langchain_core.tools import Tool

from src.config.settings import log_step
from src.services.vector_store import VectorStore

class KnowledgeBase:
    """
    Knowledge base management and querying system
    
    Handles loading, searching, and retrieving information using both direct and vector search
    """
    def __init__(self, json_path: str = "knowledge_base.json", vector_store_dir: str = "./vector_store"):
        """
        Initialize knowledge base and vector store
        
        Args:
            json_path (str): Path to knowledge base JSON file
            vector_store_dir (str): Directory for vector store
        """
        try:
            # Load JSON data
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Initialize vector store
            self.vector_store = VectorStore(vector_store_dir)
            
            # Process documents for vector store
            self._initialize_vector_store()
            
            # Create traditional search mappings
            self._create_topic_mappings()
            
            log_step('success', f"Knowledge base loaded successfully with {len(self.data['topics'])} topics")
            log_step('info', f"Available topics: {list(self.data['topics'].keys())}")
            
        except Exception as e:
            log_step('error', f"Failed to load knowledge base: {e}")
            self.data = {"topics": {}, "articles": {}}
            self.topic_aliases = {}
            self.article_aliases = {}
            raise

    def _initialize_vector_store(self):
        """Initialize vector store with documents from JSON data"""
        try:
            # Convert JSON data to documents
            documents = self.vector_store.process_json_data(self.data)
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            log_step('success', "Vector store initialized successfully")
        except Exception as e:
            log_step('error', f"Failed to initialize vector store: {e}")
            raise

    def _create_topic_mappings(self):
        """Create mappings for traditional search"""
        self.topic_aliases = {}
        for category in self.data["topics"]:
            for topic in self.data["topics"][category]:
                self.topic_aliases[topic.lower()] = (category, topic)

    def search(self, query: str, search_type: str = "hybrid", k: int = 3) -> str:
        """
        Search the knowledge base using specified search type
        
        Args:
            query: Search query
            search_type: Type of search ("vector", "traditional", or "hybrid")
            k: Number of results for vector search
            
        Returns:
            str: Formatted search results
        """
        try:
            if search_type == "vector":
                return self._vector_search(query, k)
            elif search_type == "traditional":
                return self._traditional_search(query)
            else:  # hybrid search
                vector_results = self._vector_search(query, k)
                traditional_results = self._traditional_search(query)
                return self._combine_search_results(vector_results, traditional_results)
        except Exception as e:
            log_step('error', f"Search failed: {e}")
            return f"Search failed: {str(e)}"

    def _vector_search(self, query: str, k: int = 3) -> str:
        """Perform vector similarity search"""
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            if not docs:
                return "No relevant information found."
            
            results = []
            for doc in docs:
                results.append(doc.page_content)
            
            return "\n\n".join(results)
        except Exception as e:
            log_step('error', f"Vector search failed: {e}")
            return f"Vector search failed: {str(e)}"

    def _traditional_search(self, query: str) -> str:
        """Perform traditional keyword search"""
        query_lower = query.lower()
        
        # Direct topic match
        for alias, (category, topic) in self.topic_aliases.items():
            if alias in query_lower:
                topic_data = self.data["topics"][category][topic]
                return self._format_topic_data(topic, topic_data)
        
        return "No direct matches found in topics."

    def _combine_search_results(self, vector_results: str, traditional_results: str) -> str:
        """Combine results from both search methods"""
        if "No" in traditional_results and "No" in vector_results:
            return "No relevant information found in the knowledge base."
        
        results = []
        if "No" not in traditional_results:
            results.append("Direct Matches:\n" + traditional_results)
        if "No" not in vector_results:
            results.append("Related Information:\n" + vector_results)
        
        return "\n\n".join(results)

    def _format_topic_data(self, topic: str, data: dict) -> str:
        """Format topic data for output"""
        lines = [f"Information about {topic}:"]
        
        if "definition" in data:
            lines.append(f"\nDefinition: {data['definition']}")
        
        if "history" in data:
            lines.append(f"\nHistory: {data['history']}")
        
        if "key_concepts" in data:
            lines.append("\nKey Concepts:")
            lines.extend([f"- {concept}" for concept in data["key_concepts"]])
        
        if "important_figures" in data:
            lines.append("\nImportant Figures:")
            lines.extend([f"- {figure}" for figure in data["important_figures"]])
        
        if "cultural_significance" in data:
            lines.append(f"\nCultural Significance: {data['cultural_significance']}")
        
        return "\n".join(lines)

def create_knowledge_tools(kb) -> list[Tool]:
    """Creates the enhanced knowledge base tools"""
    return [
        Tool(
            name="search_topic",
            description="""Search for information using vector, traditional, or hybrid search.
            Format: 'query|search_type' (e.g., 'Jedi training|vector' or just 'Jedi training' for hybrid)""",
            func=lambda x: kb.search(*x.split('|')) if '|' in x else kb.search(x)
        ),
        Tool(
            name="list_topics",
            description="List all available topics in the knowledge base",
            func=lambda: f"Available topics: {list(kb.topic_aliases.keys())}"
        ),
        Tool(
            name="get_article",
            description="Get a specific article by its title",
            func=lambda x: kb.search(x, search_type="traditional")
        )
    ]