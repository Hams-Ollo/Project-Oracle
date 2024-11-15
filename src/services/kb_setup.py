"""Setup script for knowledge base directory structure"""
import os
import shutil
from pathlib import Path

def setup_kb_structure():
    """Create and organize knowledge base directory structure"""
    # Define paths
    kb_dir = Path("knowledge_base")
    markdown_dir = kb_dir / "markdown"
    vectors_dir = kb_dir / "vectors"
    
    # Create directories
    markdown_dir.mkdir(parents=True, exist_ok=True)
    vectors_dir.mkdir(parents=True, exist_ok=True)
    
    # Move knowledge_base.json if it exists in root
    root_json = Path("knowledge_base.json")
    kb_json = kb_dir / "knowledge_base.json"
    if root_json.exists():
        shutil.move(str(root_json), str(kb_json))
        print(f"Moved knowledge_base.json to {kb_json}")
    
    # Move any markdown files from root knowledge_base dir to markdown subdir
    for file in kb_dir.glob("*.md"):
        if file.parent == kb_dir:  # Only move files in root of knowledge_base
            target = markdown_dir / file.name
            shutil.move(str(file), str(target))
            print(f"Moved {file.name} to {target}")

if __name__ == "__main__":
    setup_kb_structure() 