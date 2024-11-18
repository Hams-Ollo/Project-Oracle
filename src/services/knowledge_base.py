"""Enhanced Knowledge Base with vector store and multi-source support"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .kb_config import KBConfig
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .knowledge_graph import KnowledgeGraph
from langchain.tools import Tool

class KnowledgeBase:
    """Enhanced Knowledge Base with vector store and multi-source support"""
    
    def __init__(self, config: Optional[KBConfig] = None):
        """Initialize the enhanced knowledge base
        
        Args:
            config: Optional KBConfig instance for configuration
        """
        # Initialize configuration
        self.config = config if config else KBConfig()
            
        # Create required directories
        self.config.base_dir.mkdir(parents=True, exist_ok=True)
        if self.config.markdown_dir:
            self.config.markdown_dir.mkdir(parents=True, exist_ok=True)
        if self.config.vectors_dir:
            self.config.vectors_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.doc_processor = DocumentProcessor(self.config)
        self.vector_store = VectorStore(self.config)
        self.knowledge_graph = KnowledgeGraph(self.config)
        
        # Source tracking
        self.source_map = {}
        
        # Load initial content
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize knowledge base with all available content"""
        # Process JSON knowledge base
        if self.config.knowledge_base_path.exists():
            try:
                doc = self.doc_processor.process_document(self.config.knowledge_base_path)
                chunk_ids = self.vector_store.add_document(doc)
                self._update_source_map(doc, chunk_ids)
            except Exception as e:
                logging.error(f"Error processing knowledge base JSON: {str(e)}")
        
        # Process documentation directory
        try:
            if self.config.markdown_dir.exists():
                for doc in self.doc_processor.process_directory(self.config.markdown_dir):
                    chunk_ids = self.vector_store.add_document(doc)
                    self._update_source_map(doc, chunk_ids)
        except Exception as e:
            logging.error(f"Error processing documentation: {str(e)}")
    
    def _update_source_map(self, doc: Any, chunk_ids: List[str]):
        """Update source mapping for document chunks"""
        for chunk_id in chunk_ids:
            self.source_map[chunk_id] = {
                "source": doc.metadata["source"],
                "type": doc.metadata["type"],
                "doc_type": doc.doc_type,
                "processed_at": datetime.now().isoformat()
            }
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        doc_type: Optional[str] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge base with optional filters
        
        Args:
            query: Search query
            limit: Maximum number of results
            doc_type: Filter by document type
            min_score: Minimum similarity score
            
        Returns:
            List of search results with metadata
        """
        # Prepare filters
        filters = {}
        if doc_type:
            filters["doc_type"] = doc_type
            
        # Perform search
        results = self.vector_store.search(
            query=query,
            limit=limit,
            filters=filters,
            min_score=min_score
        )
        
        # Format results with source information
        formatted_results = []
        for i, (content, metadata, doc_id) in enumerate(zip(
            results["documents"],
            results["metadatas"],
            results["ids"]
        )):
            source_info = self.source_map.get(doc_id, {})
            formatted_results.append({
                "content": content,
                "source": source_info.get("source", "Unknown"),
                "doc_type": source_info.get("doc_type", "Unknown"),
                "metadata": metadata,
                "score": 1 - results["distances"][i],  # Convert distance to similarity score
                "citation": self._generate_citation(doc_id)
            })
            
        return formatted_results
    
    def _generate_citation(self, doc_id: str) -> Optional[str]:
        """Generate citation for a document chunk"""
        source_info = self.source_map.get(doc_id)
        if not source_info:
            return None
            
        source_path = Path(source_info["source"])
        if source_info["type"] == "json":
            return f"Knowledge Base JSON, Section: {source_path.stem}"
        else:
            return f"{source_path.stem} ({source_info['doc_type']})"
    
    def add_document(self, file_path: str) -> bool:
        """Add a new document to the knowledge base
        
        Args:
            file_path: Path to document file
            
        Returns:
            bool: Success status
        """
        try:
            doc = self.doc_processor.process_document(Path(file_path))
            chunk_ids = self.vector_store.add_document(doc)
            self._update_source_map(doc, chunk_ids)
            return True
        except Exception as e:
            logging.error(f"Error adding document {file_path}: {str(e)}")
            return False
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data if found
        """
        return self.vector_store.get_document(doc_id)
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get list of all documents in the knowledge base
        
        Returns:
            List of documents with metadata
        """
        documents = []
        unique_sources = set()
        
        for chunk_id, metadata in self.source_map.items():
            source = metadata["source"]
            if source not in unique_sources:
                documents.append({
                    "title": Path(source).stem,
                    "source": source,
                    "type": metadata["type"],
                    "doc_type": metadata["doc_type"],
                    "processed_at": metadata["processed_at"]
                })
                unique_sources.add(source)
        
        return sorted(documents, key=lambda x: x["processed_at"], reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics
        
        Returns:
            Statistics about the knowledge base
        """
        return {
            "total_documents": len(self.source_map),
            "document_types": self._count_doc_types(),
            "last_updated": max(
                info["processed_at"] 
                for info in self.source_map.values()
            ) if self.source_map else None
        }
    
    def _count_doc_types(self) -> Dict[str, int]:
        """Count documents by type"""
        counts = {}
        for info in self.source_map.values():
            doc_type = info["doc_type"]
            counts[doc_type] = counts.get(doc_type, 0) + 1
        return counts
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Search documents by tag"""
        return self.vector_store.search(
            query="",
            filters={"tags": {"$contains": tag}}
        )
    
    def find_internal_links(self, content: str) -> List[str]:
        """Find internal references in content"""
        references = []
        for doc_id in self.source_map:
            if doc_id in content:
                references.append(self.get_document_by_id(doc_id))
        return references

def create_knowledge_tools(kb: KnowledgeBase) -> List[Tool]:
    """Create tools for interacting with the knowledge base
    
    Args:
        kb: KnowledgeBase instance
        
    Returns:
        List of LangChain tools
    """
    return [
        Tool(
            name="search_knowledge_base",
            description="Search the knowledge base for information",
            func=lambda q: kb.search(
                query=q,
                limit=5
            )
        ),
        Tool(
            name="get_document",
            description="Retrieve a specific document by ID",
            func=kb.get_document_by_id
        ),
        Tool(
            name="get_kb_statistics",
            description="Get statistics about the knowledge base",
            func=kb.get_statistics
        )
    ]