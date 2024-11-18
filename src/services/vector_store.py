"""Vector store for document embeddings and similarity search"""
import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

class VectorStore:
    """Vector store implementation using ChromaDB"""
    
    def __init__(self, config):
        """Initialize vector store
        
        Args:
            config: Knowledge base configuration
        """
        self.config = config
        self.client = None
        self.collection = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize ChromaDB and collection"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.config.vector_store_path)
            )
            
            # Initialize embedding function
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"  # Changed from text-embedding-ada-002
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            
            logging.info("Vector store initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_document(self, doc) -> List[str]:
        """Add document to vector store
        
        Args:
            doc: Processed document
            
        Returns:
            List of chunk IDs
        """
        try:
            # Add document chunks to collection
            self.collection.add(
                documents=doc.chunks,
                metadatas=[doc.metadata] * len(doc.chunks),
                ids=[f"{doc.source_id}_{i}" for i in range(len(doc.chunks))]
            )
            return [f"{doc.source_id}_{i}" for i in range(len(doc.chunks))]
        except Exception as e:
            logging.error(f"Error adding document to vector store: {str(e)}")
            raise
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        filters: Optional[Dict] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Search for similar documents
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            Search results
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit or 10,
                where=filters
            )
            return results
        except Exception as e:
            logging.error(f"Error searching vector store: {str(e)}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data if found
        """
        try:
            results = self.collection.get(
                ids=[doc_id]
            )
            if results["documents"]:
                return {
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0]
                }
            return None
        except Exception as e:
            logging.error(f"Error retrieving document: {str(e)}")
            return None