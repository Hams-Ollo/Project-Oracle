"""Configuration for Knowledge Base with enhanced features"""
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class KBConfig(BaseModel):
    """Configuration for knowledge base components"""
    base_dir: Path = Field(default_factory=lambda: Path("knowledge_base"))
    vector_store_path: Optional[Path] = None
    knowledge_base_path: Optional[Path] = None
    markdown_dir: Optional[Path] = None
    vectors_dir: Optional[Path] = None
    graph_dir: Optional[Path] = None
    chunk_size: int = 1000
    chunk_overlap: int = 200
    relationship_types: List[str] = Field(
        default_factory=lambda: [
            "references",
            "related_to",
            "depends_on",
            "part_of",
            "see_also"
        ]
    )

    def model_post_init(self, __context):
        """Post initialization processing to set up derived paths"""
        # Convert string paths to Path objects if needed
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)
            
        # Set up default paths relative to base_dir
        if not self.vector_store_path:
            self.vector_store_path = self.base_dir / "vector_store"
        if not self.knowledge_base_path:
            self.knowledge_base_path = self.base_dir / "knowledge_base.json"
        if not self.markdown_dir:
            self.markdown_dir = self.base_dir / "markdown"
        if not self.vectors_dir:
            self.vectors_dir = self.base_dir / "vectors"
        if not self.graph_dir:
            self.graph_dir = self.base_dir / "graph"

    class Config:
        arbitrary_types_allowed = True