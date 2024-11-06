import os
from pathlib import Path
from typing import Dict, List, Optional
import markdown
import re
from enum import Enum

class DocCategory(Enum):
    ONBOARDING = ["USER_GUIDE", "CONTRIBUTING", "GIT_BRANCHING"]
    TECHNICAL = ["API", "ARCHITECTURE", "DEPLOYMENT", "SECURITY"]
    PROCESS = ["TESTING", "PERFORMANCE", "TROUBLESHOOTING"]
    GENERAL = ["CHANGELOG"]

class DocumentationLoader:
    def __init__(self, docs_path: str = "docs"):
        self.docs_path = docs_path
        self.docs_cache: Dict[str, str] = {}
        self.last_update: Dict[str, float] = {}
        self.doc_categories: Dict[str, DocCategory] = self._categorize_docs()
    
    def _categorize_docs(self) -> Dict[str, DocCategory]:
        """Map documents to their categories"""
        doc_categories = {}
        for doc_path in Path(self.docs_path).glob('**/*.md'):
            doc_name = doc_path.stem.upper()
            for category in DocCategory:
                if doc_name in category.value:
                    doc_categories[doc_name] = category
                    break
            if doc_name not in doc_categories:
                doc_categories[doc_name] = DocCategory.GENERAL
        return doc_categories

    def load_markdown_file(self, filepath: str) -> Dict[str, str]:
        """Load and convert markdown file to plain text with sections"""
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Split content into sections based on headers
            sections = {}
            current_section = "overview"
            current_content = []
            
            for line in content.split('\n'):
                if line.startswith('#'):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line.lstrip('#').strip().lower()
                    current_content = []
                else:
                    current_content.append(line)
            
            # Add the last section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            return sections
    
    def get_all_docs(self) -> Dict[str, Dict[str, str]]:
        """Load all markdown files from docs directory with their sections"""
        docs = {}
        docs_dir = Path(self.docs_path)
        
        if not docs_dir.exists():
            print(f"[WARNING] Documentation directory {self.docs_path} not found")
            return docs
        
        for file_path in docs_dir.glob('**/*.md'):
            current_mtime = os.path.getmtime(file_path)
            cached_mtime = self.last_update.get(str(file_path), 0)
            
            if current_mtime > cached_mtime:
                try:
                    sections = self.load_markdown_file(str(file_path))
                    docs[file_path.stem] = sections
                    self.docs_cache[str(file_path)] = sections
                    self.last_update[str(file_path)] = current_mtime
                except Exception as e:
                    print(f"[ERROR] Failed to load {file_path}: {str(e)}")
            else:
                docs[file_path.stem] = self.docs_cache[str(file_path)]
        
        return docs

    def get_relevant_docs(self, query: str, context_type: str = None) -> List[Dict[str, str]]:
        """Retrieve relevant documentation based on query and context"""
        docs = self.get_all_docs()
        relevant_docs = []
        
        # Convert context_type to DocCategory
        target_category = None
        if context_type:
            try:
                target_category = DocCategory[context_type.upper()]
            except KeyError:
                pass
        
        # Prepare query terms
        query_terms = set(query.lower().split())
        
        for doc_name, sections in docs.items():
            # Check category relevance
            if target_category and self.doc_categories.get(doc_name.upper()) != target_category:
                continue
            
            # Score each section's relevance
            relevant_sections = {}
            for section_name, content in sections.items():
                content_lower = content.lower()
                relevance_score = sum(term in content_lower for term in query_terms)
                
                if relevance_score > 0:
                    relevant_sections[section_name] = content
            
            if relevant_sections:
                relevant_docs.append({
                    "doc_name": doc_name,
                    "category": self.doc_categories.get(doc_name.upper(), DocCategory.GENERAL).name,
                    "sections": relevant_sections
                })
        
        return sorted(relevant_docs, key=lambda x: len(x["sections"]), reverse=True)

    def get_doc_by_category(self, category: DocCategory) -> List[Dict[str, str]]:
        """Get all documents for a specific category"""
        docs = self.get_all_docs()
        category_docs = []
        
        for doc_name, sections in docs.items():
            if self.doc_categories.get(doc_name.upper()) == category:
                category_docs.append({
                    "doc_name": doc_name,
                    "sections": sections
                })
        
        return category_docs