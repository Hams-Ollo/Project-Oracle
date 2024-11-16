"""Configuration for Knowledge Base with enhanced features"""
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class KBConfig(BaseModel):
    """Enhanced Knowledge Base Configuration"""
    # Base paths
    base_dir: Path = Field(default=Path("knowledge_base"))
    json_path: Path = Field(default=None)
    markdown_dir: Path = Field(default=None)
    vectors_dir: Path = Field(default=None)
    docs_dir: Path = Field(default=None)
    versions_dir: Path = Field(default=None)  # New: Version control directory
    graph_dir: Path = Field(default=None)     # New: Knowledge graph storage
    
    # Processing settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    
    # Vector store settings
    vector_store_type: str = Field(default="chroma")
    similarity_threshold: float = Field(default=0.7)
    
    # New: Version control settings
    version_control: bool = Field(default=True)
    max_versions: int = Field(default=10)
    version_naming: str = Field(default="timestamp")  # Options: timestamp, semantic
    
    # New: Metadata settings
    metadata_schema: Dict = Field(
        default={
            "title": str,
            "tags": List[str],
            "created_at": str,
            "modified_at": str,
            "version": str,
            "author": str,
            "references": List[str],
            "status": str,  # draft, published, archived
            "type": str,    # note, article, image, etc.
        }
    )
    
    # New: Knowledge graph settings
    graph_backend: str = Field(default="networkx")  # Options: networkx, neo4j
    relationship_types: List[str] = Field(
        default=[
            "references",
            "related_to",
            "depends_on",
            "inspired_by",
            "contradicts",
            "supports"
        ]
    )
    
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
        if self.versions_dir is None:
            self.versions_dir = self.base_dir / "versions"
        if self.graph_dir is None:
            self.graph_dir = self.base_dir / "graph"
    
    class Config:
        arbitrary_types_allowed = True