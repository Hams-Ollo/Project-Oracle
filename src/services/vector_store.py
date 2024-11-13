"""
Vector store service for document storage and retrieval.
"""

from pathlib import Path
from typing import List, Dict
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from src.config.settings import log_step

class VectorStore:
    """Vector store for document storage and similarity search"""
    
    def __init__(self, persist_dir: str = "vector_store"):
        """
        Initialize vector store
        
        Args:
            persist_dir (str): Directory for storing vector data
        """
        self.persist_dir = Path(persist_dir)
        self.embeddings = OpenAIEmbeddings()
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        try:
            self.store = Chroma(
                persist_directory=str(self.persist_dir),
                embedding_function=self.embeddings
            )
            log_step('success', f"Vector store initialized at {self.persist_dir}")
        except Exception as e:
            log_step('error', f"Failed to initialize vector store: {e}")
            raise

    def process_json_data(self, data: Dict) -> List[Document]:
        """
        Convert JSON data to documents for vector store
        
        Args:
            data (Dict): Knowledge base data
            
        Returns:
            List[Document]: Processed documents
        """
        documents = []
        
        # Process topics
        for category, topics in data["topics"].items():
            for topic_name, topic_data in topics.items():
                # Create main topic document
                content = f"Category: {category}\nTopic: {topic_name}\n"
                if "definition" in topic_data:
                    content += f"Definition: {topic_data['definition']}\n"
                if "history" in topic_data:
                    content += f"History: {topic_data['history']}\n"
                
                # Add key concepts and important figures if available
                if "key_concepts" in topic_data:
                    content += f"Key Concepts: {', '.join(topic_data['key_concepts'])}\n"
                if "important_figures" in topic_data:
                    content += f"Important Figures: {', '.join(topic_data['important_figures'])}\n"
                if "cultural_significance" in topic_data:
                    content += f"Cultural Significance: {topic_data['cultural_significance']}"
                
                documents.append(Document(
                    page_content=content,
                    metadata={"category": category, "topic": topic_name, "type": "topic"}
                ))
        
        # Process articles if they exist
        if "articles" in data:
            for category, articles in data["articles"].items():
                for article_name, article_data in articles.items():
                    content = f"Category: {category}\nArticle: {article_name}\n"
                    if "title" in article_data:
                        content += f"Title: {article_data['title']}\n"
                    if "summary" in article_data:
                        content += f"Summary: {article_data['summary']}\n"
                    if "content" in article_data:
                        content += f"Content: {article_data['content']}"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={"category": category, "article": article_name, "type": "article"}
                    ))
        
        return documents

    def add_documents(self, documents: List[Document]):
        """
        Add documents to vector store
        
        Args:
            documents (List[Document]): Documents to add
        """
        try:
            if documents:
                self.store.add_documents(documents)
                log_step('success', f"Added {len(documents)} chunks to vector store")
            else:
                log_step('warning', "No documents to add")
        except Exception as e:
            log_step('error', f"Failed to add documents: {e}")
            raise

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Document]: Similar documents
        """
        try:
            return self.store.similarity_search(query, k=k)
        except Exception as e:
            log_step('error', f"Similarity search failed: {e}")
            raise