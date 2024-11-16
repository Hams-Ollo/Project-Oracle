"""Advanced search engine with hybrid search capabilities and document indexing"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
import numpy as np
from dataclasses import dataclass

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.retrievers import BM25Retriever
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from sklearn.metrics.pairwise import cosine_similarity

from .document_processor import ProcessedDocument
from .kb_config import KBConfig

@dataclass
class SearchResult:
    """Container for search results with relevance scoring"""
    document_id: str
    chunk_content: str
    relevance_score: float
    semantic_score: float
    keyword_score: float
    metadata: Dict[str, Any]
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None

class SearchEngine:
    """Advanced search engine with hybrid search capabilities"""
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=0)
        self.vector_store = None
        self.bm25_retriever = None
        self.document_index: Dict[str, ProcessedDocument] = {}
        
    def index_documents(self, documents: List[ProcessedDocument]):
        """Index documents for both semantic and keyword search
        
        Args:
            documents: List of processed documents to index
        """
        # Convert ProcessedDocuments to Langchain Documents
        langchain_docs = []
        for doc in documents:
            self.document_index[doc.source_id] = doc
            for chunk in doc.chunks:
                langchain_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source_id": doc.source_id,
                            "doc_type": doc.doc_type,
                            **doc.metadata
                        }
                    )
                )
        
        # Initialize or update vector store
        if self.vector_store is None:
            self.vector_store = Chroma.from_documents(
                documents=langchain_docs,
                embedding=self.embeddings,
                persist_directory=str(self.config.vector_store_path)
            )
        else:
            self.vector_store.add_documents(langchain_docs)
            
        # Initialize BM25 retriever for keyword search
        self.bm25_retriever = BM25Retriever.from_documents(langchain_docs)
        
        logging.info(f"Indexed {len(documents)} documents with {len(langchain_docs)} chunks")
        
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        min_relevance: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Perform hybrid search combining semantic and keyword-based approaches
        
        Args:
            query: Search query
            k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
            min_relevance: Minimum relevance score (0-1)
            filters: Optional metadata filters
            
        Returns:
            List of search results with relevance scores
        """
        # Normalize weights
        total_weight = semantic_weight + keyword_weight
        semantic_weight = semantic_weight / total_weight
        keyword_weight = keyword_weight / total_weight
        
        # Get semantic search results
        semantic_docs = self.vector_store.similarity_search_with_relevance_scores(
            query,
            k=k * 2,  # Get more results for hybrid ranking
            filter=filters
        )
        
        # Get keyword search results
        keyword_docs = self.bm25_retriever.get_relevant_documents(query)[:k * 2]
        
        # Combine and rank results
        results = {}
        
        # Process semantic results
        query_embedding = self.embeddings.embed_query(query)
        for doc, score in semantic_docs:
            results[doc.metadata["source_id"]] = {
                "chunk": doc.page_content,
                "semantic_score": score,
                "keyword_score": 0.0,
                "metadata": doc.metadata
            }
            
        # Process keyword results
        for i, doc in enumerate(keyword_docs):
            doc_id = doc.metadata["source_id"]
            keyword_score = 1.0 - (i / len(keyword_docs))  # Normalize score
            if doc_id in results:
                results[doc_id]["keyword_score"] = keyword_score
            else:
                results[doc_id] = {
                    "chunk": doc.page_content,
                    "semantic_score": 0.0,
                    "keyword_score": keyword_score,
                    "metadata": doc.metadata
                }
                
        # Calculate final scores and create SearchResult objects
        search_results = []
        for doc_id, result in results.items():
            relevance_score = (
                semantic_weight * result["semantic_score"] +
                keyword_weight * result["keyword_score"]
            )
            
            if relevance_score >= min_relevance:
                # Get original document for additional context
                orig_doc = self.document_index.get(doc_id)
                search_results.append(
                    SearchResult(
                        document_id=doc_id,
                        chunk_content=result["chunk"],
                        relevance_score=relevance_score,
                        semantic_score=result["semantic_score"],
                        keyword_score=result["keyword_score"],
                        metadata=result["metadata"],
                        summary=orig_doc.summary if orig_doc else None,
                        key_points=orig_doc.key_points if orig_doc else None
                    )
                )
                
        # Sort by relevance score
        search_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return search_results[:k]
        
    def find_related_documents(
        self,
        document_id: str,
        k: int = 5,
        min_similarity: float = 0.3
    ) -> List[SearchResult]:
        """Find documents related to a given document
        
        Args:
            document_id: ID of the source document
            k: Number of related documents to return
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of related documents with similarity scores
        """
        source_doc = self.document_index.get(document_id)
        if not source_doc:
            raise ValueError(f"Document not found: {document_id}")
            
        # Get embeddings for source document chunks
        source_chunks = [
            Document(page_content=chunk)
            for chunk in source_doc.chunks
        ]
        source_embeddings = self.embeddings.embed_documents(
            [doc.page_content for doc in source_chunks]
        )
        
        # Find similar documents
        similar_docs = self.vector_store.similarity_search_with_relevance_scores(
            source_chunks[0].page_content,  # Use first chunk as query
            k=k * 2
        )
        
        results = []
        for doc, score in similar_docs:
            if doc.metadata["source_id"] != document_id and score >= min_similarity:
                orig_doc = self.document_index.get(doc.metadata["source_id"])
                results.append(
                    SearchResult(
                        document_id=doc.metadata["source_id"],
                        chunk_content=doc.page_content,
                        relevance_score=score,
                        semantic_score=score,
                        keyword_score=0.0,
                        metadata=doc.metadata,
                        summary=orig_doc.summary if orig_doc else None,
                        key_points=orig_doc.key_points if orig_doc else None
                    )
                )
                
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:k]
        
    def analyze_document_relationships(self, min_similarity: float = 0.5) -> Dict[str, List[str]]:
        """Analyze relationships between all documents in the index
        
        Args:
            min_similarity: Minimum similarity score to consider documents related
            
        Returns:
            Dictionary mapping document IDs to lists of related document IDs
        """
        relationships = {}
        doc_ids = list(self.document_index.keys())
        
        for doc_id in doc_ids:
            related = self.find_related_documents(
                doc_id,
                k=5,
                min_similarity=min_similarity
            )
            relationships[doc_id] = [
                result.document_id
                for result in related
            ]
            
        return relationships
