"""Enhanced metadata management for knowledge base articles"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ArticleMetadata(BaseModel):
    """Metadata model for knowledge base articles"""
    title: str
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    author: Optional[str] = None
    references: List[str] = Field(default_factory=list)
    status: str = "draft"  # draft, published, archived
    type: str = "note"     # note, article, image, etc.
    
    @validator('tags', 'references', pre=True)
    def ensure_list(cls, v):
        """Ensure tags and references are lists"""
        if isinstance(v, str):
            return [v]
        return v

class MetadataManager:
    """Manages metadata for knowledge base articles"""
    
    def __init__(self, config):
        """Initialize metadata manager
        
        Args:
            config: KBConfig instance
        """
        self.config = config
        self.metadata_file = config.base_dir / "metadata.json"
        self.metadata_cache = self._load_metadata_cache()
        
    def get_metadata(self, file_path: Path) -> ArticleMetadata:
        """Get metadata for an article
        
        Args:
            file_path: Path to the article
            
        Returns:
            ArticleMetadata: Article metadata
        """
        if str(file_path) in self.metadata_cache:
            return ArticleMetadata(**self.metadata_cache[str(file_path)])
        return self._create_default_metadata(file_path)
        
    def update_metadata(self, file_path: Path, updates: Dict[str, Any]) -> ArticleMetadata:
        """Update metadata for an article
        
        Args:
            file_path: Path to the article
            updates: Metadata updates
            
        Returns:
            ArticleMetadata: Updated metadata
        """
        current = self.get_metadata(file_path)
        updated = current.copy(update=updates)
        updated.modified_at = datetime.now().isoformat()
        
        self.metadata_cache[str(file_path)] = updated.dict()
        self._save_metadata_cache()
        
        return updated
        
    def add_tags(self, file_path: Path, tags: List[str]) -> ArticleMetadata:
        """Add tags to an article
        
        Args:
            file_path: Path to the article
            tags: Tags to add
            
        Returns:
            ArticleMetadata: Updated metadata
        """
        current = self.get_metadata(file_path)
        current_tags = set(current.tags)
        current_tags.update(tags)
        
        return self.update_metadata(file_path, {"tags": list(current_tags)})
        
    def add_references(self, file_path: Path, references: List[str]) -> ArticleMetadata:
        """Add references to an article
        
        Args:
            file_path: Path to the article
            references: References to add
            
        Returns:
            ArticleMetadata: Updated metadata
        """
        current = self.get_metadata(file_path)
        current_refs = set(current.references)
        current_refs.update(references)
        
        return self.update_metadata(file_path, {"references": list(current_refs)})
        
    def search_by_metadata(self, **criteria) -> List[Path]:
        """Search articles by metadata criteria
        
        Args:
            **criteria: Metadata search criteria
            
        Returns:
            List[Path]: Matching file paths
        """
        results = []
        for file_path, metadata in self.metadata_cache.items():
            matches = True
            for key, value in criteria.items():
                if key not in metadata:
                    matches = False
                    break
                if isinstance(value, list):
                    if not all(v in metadata[key] for v in value):
                        matches = False
                        break
                elif metadata[key] != value:
                    matches = False
                    break
            if matches:
                results.append(Path(file_path))
        return results
        
    def _create_default_metadata(self, file_path: Path) -> ArticleMetadata:
        """Create default metadata for a new article"""
        metadata = ArticleMetadata(
            title=file_path.stem,
            type=self._guess_type(file_path)
        )
        self.metadata_cache[str(file_path)] = metadata.dict()
        self._save_metadata_cache()
        return metadata
        
    def _guess_type(self, file_path: Path) -> str:
        """Guess article type from file extension"""
        ext = file_path.suffix.lower()
        if ext in ['.md', '.txt']:
            return 'note'
        elif ext in ['.pdf', '.docx']:
            return 'document'
        elif ext in ['.jpg', '.png', '.jpeg']:
            return 'image'
        elif ext in ['.mp3', '.wav']:
            return 'audio'
        return 'unknown'
        
    def _load_metadata_cache(self) -> Dict:
        """Load metadata cache from disk"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def _save_metadata_cache(self):
        """Save metadata cache to disk"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata_cache, f, indent=2)
