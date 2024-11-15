"""Enhanced document processing for Knowledge Base"""
from pathlib import Path
from typing import List, Dict, Any, Generator
import json
import logging
from dataclasses import dataclass
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader

from .kb_config import KBConfig

@dataclass
class ProcessedDocument:
    """Container for processed document chunks and metadata"""
    chunks: List[str]
    metadata: Dict[str, Any]
    source_id: str
    doc_type: str

class DocumentProcessor:
    """Enhanced document processor with metadata extraction"""
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
        )
        
    def process_markdown_directory(self) -> Generator[ProcessedDocument, None, None]:
        """Process all markdown files in the knowledge base"""
        if not self.config.markdown_dir.exists():
            logging.warning(f"Markdown directory not found: {self.config.markdown_dir}")
            return

        for file_path in self.config.markdown_dir.rglob("*.md"):
            try:
                yield self._process_markdown_file(file_path)
            except Exception as e:
                logging.error(f"Error processing markdown file {file_path}: {str(e)}")
                
    def _process_markdown_file(self, file_path: Path) -> ProcessedDocument:
        """Process a single markdown file with metadata extraction"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract metadata from markdown frontmatter if present
        metadata = self._extract_markdown_metadata(content)
        clean_content = self._remove_frontmatter(content)
        
        # Extract title from first heading
        title = self._extract_title(clean_content) or file_path.stem
        
        # Generate chunks
        chunks = self.text_splitter.split_text(clean_content)
        
        return ProcessedDocument(
            chunks=chunks,
            metadata={
                "source": str(file_path),
                "title": title,
                "type": "markdown",
                **metadata
            },
            source_id=f"md_{file_path.stem}",
            doc_type="markdown"
        )
    
    def process_json_kb(self) -> ProcessedDocument:
        """Process the main knowledge base JSON file"""
        if not self.config.json_path.exists():
            raise FileNotFoundError(f"Knowledge base JSON not found: {self.config.json_path}")
            
        with open(self.config.json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            
        # Convert JSON structure to text chunks
        chunks = []
        for section in ["topics", "articles"]:
            section_data = content.get(section, {})
            for key, value in section_data.items():
                chunk = self._process_json_section(section, key, value)
                chunks.extend(self.text_splitter.split_text(chunk))
                
        return ProcessedDocument(
            chunks=chunks,
            metadata={
                "source": str(self.config.json_path),
                "type": "json",
                "sections": list(content.keys())
            },
            source_id="main_kb",
            doc_type="json"
        )
    
    def _process_json_section(self, section: str, key: str, value: Any) -> str:
        """Convert a JSON section to searchable text"""
        if isinstance(value, dict):
            return f"{section} - {key}:\n" + "\n".join(
                f"{k}: {v}" for k, v in value.items()
            )
        return f"{section} - {key}: {value}"
    
    def _extract_markdown_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from markdown frontmatter"""
        metadata = {}
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        return metadata
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove frontmatter from markdown content"""
        return re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    def _extract_title(self, content: str) -> str:
        """Extract title from first markdown heading"""
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return title_match.group(1) if title_match else None 

    def process_document(self, document_path: Path) -> dict:
        """Process a single document."""
        try:
            # Implementation
            pass
        except Exception as e:
            logging.error(f"Error processing document {document_path}: {str(e)}")
            raise

    def process_directory(self, directory_path: Path) -> list:
        """Process all documents in a directory."""
        try:
            # Implementation
            pass
        except Exception as e:
            logging.error(f"Error processing directory {directory_path}: {str(e)}")
            raise