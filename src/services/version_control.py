"""Version control system for knowledge base articles"""
from pathlib import Path
from typing import Dict, List, Optional
import json
import shutil
from datetime import datetime
import hashlib

class VersionControl:
    """Manages version control for knowledge base articles"""
    
    def __init__(self, config):
        """Initialize version control system
        
        Args:
            config: KBConfig instance
        """
        self.config = config
        self.versions_dir = config.versions_dir
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
    def save_version(self, content: str, metadata: Dict, file_path: Path) -> str:
        """Save a new version of an article
        
        Args:
            content: Article content
            metadata: Article metadata
            file_path: Path to the original file
            
        Returns:
            str: Version identifier
        """
        # Generate version ID
        version_id = self._generate_version_id(content, metadata)
        
        # Create version directory if needed
        article_versions_dir = self.versions_dir / file_path.stem
        article_versions_dir.mkdir(exist_ok=True)
        
        # Save content and metadata
        version_data = {
            "content": content,
            "metadata": {
                **metadata,
                "version_id": version_id,
                "created_at": datetime.now().isoformat(),
                "original_file": str(file_path)
            }
        }
        
        version_file = article_versions_dir / f"{version_id}.json"
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)
            
        # Maintain version limit
        self._cleanup_old_versions(article_versions_dir)
        
        return version_id
        
    def get_version(self, file_path: Path, version_id: str) -> Optional[Dict]:
        """Retrieve a specific version of an article
        
        Args:
            file_path: Path to the original file
            version_id: Version identifier
            
        Returns:
            Optional[Dict]: Version data if found
        """
        version_file = self.versions_dir / file_path.stem / f"{version_id}.json"
        if not version_file.exists():
            return None
            
        with open(version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def list_versions(self, file_path: Path) -> List[Dict]:
        """List all versions of an article
        
        Args:
            file_path: Path to the original file
            
        Returns:
            List[Dict]: List of version metadata
        """
        versions_dir = self.versions_dir / file_path.stem
        if not versions_dir.exists():
            return []
            
        versions = []
        for version_file in versions_dir.glob("*.json"):
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                versions.append(data["metadata"])
                
        return sorted(versions, key=lambda x: x["created_at"], reverse=True)
        
    def restore_version(self, file_path: Path, version_id: str) -> bool:
        """Restore a specific version as the current version
        
        Args:
            file_path: Path to the original file
            version_id: Version identifier
            
        Returns:
            bool: Success status
        """
        version_data = self.get_version(file_path, version_id)
        if not version_data:
            return False
            
        # Create backup of current version
        if file_path.exists():
            self.save_version(
                file_path.read_text(encoding='utf-8'),
                {"restored_from": version_id},
                file_path
            )
            
        # Restore version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(version_data["content"])
            
        return True
        
    def _generate_version_id(self, content: str, metadata: Dict) -> str:
        """Generate a unique version identifier"""
        if self.config.version_naming == "timestamp":
            return datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            # Generate content hash
            content_hash = hashlib.sha256(
                (content + str(metadata)).encode()
            ).hexdigest()[:8]
            return f"{datetime.now().strftime('%Y%m%d')}_{content_hash}"
            
    def _cleanup_old_versions(self, versions_dir: Path):
        """Remove old versions if exceeding max_versions limit"""
        versions = sorted(
            versions_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(versions) > self.config.max_versions:
            for old_version in versions[self.config.max_versions:]:
                old_version.unlink()
