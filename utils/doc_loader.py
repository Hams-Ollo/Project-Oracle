import os
from pathlib import Path
from typing import Dict, List
import markdown
import re

class DocumentationLoader:
    def __init__(self, docs_path: str = "docs"):
        self.docs_path = docs_path
        self.docs_cache: Dict[str, str] = {}
        self.last_update: Dict[str, float] = {}
    
    def load_markdown_file(self, filepath: str) -> str:
        """Load and convert markdown file to plain text"""
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            # Convert markdown to plain text while preserving structure
            html = markdown.markdown(content)
            # Remove HTML tags while keeping content
            text = re.sub('<[^<]+?>', '', html)
            return text
    
    def get_all_docs(self) -> Dict[str, str]:
        """Load all markdown files from docs directory"""
        docs = {}
        docs_dir = Path(self.docs_path)
        
        if not docs_dir.exists():
            print(f"[WARNING] Documentation directory {self.docs_path} not found")
            return docs
        
        for file_path in docs_dir.glob('**/*.md'):
            current_mtime = os.path.getmtime(file_path)
            cached_mtime = self.last_update.get(str(file_path), 0)
            
            # Only reload if file has been modified
            if current_mtime > cached_mtime:
                try:
                    content = self.load_markdown_file(str(file_path))
                    docs[file_path.stem] = content
                    self.docs_cache[str(file_path)] = content
                    self.last_update[str(file_path)] = current_mtime
                except Exception as e:
                    print(f"[ERROR] Failed to load {file_path}: {str(e)}")
            else:
                docs[file_path.stem] = self.docs_cache[str(file_path)]
        
        return docs

    def get_relevant_docs(self, query: str, context_type: str = None) -> List[str]:
        """Retrieve relevant documentation based on query and context"""
        docs = self.get_all_docs()
        relevant_docs = []
        
        # Simple keyword matching for now
        # This could be enhanced with proper embedding-based search later
        query_terms = query.lower().split()
        
        for doc_name, content in docs.items():
            # If context_type is specified, only look in relevant docs
            if context_type:
                if context_type.lower() not in doc_name.lower():
                    continue
            
            # Check if query terms appear in content
            if any(term in content.lower() for term in query_terms):
                relevant_docs.append(content)
        
        return relevant_docs 