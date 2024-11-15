"""Configuration for Knowledge Base"""
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List

class KBConfig(BaseModel):
    """Knowledge Base Configuration"""
    # Base paths
    base_dir: Path = Field(default=Path("knowledge_base"))
    json_path: Path = Field(default=None)
    markdown_dir: Path = Field(default=None)
    vectors_dir: Path = Field(default=None)
    docs_dir: Path = Field(default=None)
    
    # Processing settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    
    # Vector store settings
    vector_store_type: str = Field(default="chroma")
    similarity_threshold: float = Field(default=0.7)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set default paths relative to base_dir if not provided
        if self.json_path is None:
            self.json_path = self.base_dir / "knowledge_base.json"
        if self.markdown_dir is None:
            self.markdown_dir = self.base_dir / "markdown"
        if self.vectors_dir is None:
            self.vectors_dir = self.base_dir / "vectors"
        if self.docs_dir is None:
            self.docs_dir = self.base_dir / "docs"
    
    class Config:
        arbitrary_types_allowed = True 