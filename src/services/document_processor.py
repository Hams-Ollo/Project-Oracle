"""Enhanced document processing with multi-format support and advanced features"""
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
import json
import logging
from dataclasses import dataclass
import re
from datetime import datetime

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter,
)
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredImageLoader,
)
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI

from .kb_config import KBConfig

@dataclass
class ProcessedDocument:
    """Container for processed document chunks and metadata"""
    chunks: List[str]
    metadata: Dict[str, Any]
    source_id: str
    doc_type: str
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    processed_at: str = datetime.now().isoformat()

class DocumentProcessor:
    """Enhanced document processor with multi-format support"""
    
    SUPPORTED_FORMATS = {
        ".txt": (TextLoader, RecursiveCharacterTextSplitter),
        ".md": (TextLoader, MarkdownTextSplitter),
        ".pdf": (PyPDFLoader, RecursiveCharacterTextSplitter),
        ".docx": (Docx2txtLoader, RecursiveCharacterTextSplitter),
        ".png": (UnstructuredImageLoader, RecursiveCharacterTextSplitter),
        ".jpg": (UnstructuredImageLoader, RecursiveCharacterTextSplitter),
        ".jpeg": (UnstructuredImageLoader, RecursiveCharacterTextSplitter),
    }
    
    def __init__(self, config: KBConfig):
        self.config = config
        self.llm = ChatOpenAI(temperature=0)  # For summarization
        self.default_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
        )
        
    def process_document(self, document_path: Path) -> ProcessedDocument:
        """Process a document with automatic format detection and summarization
        
        Args:
            document_path: Path to the document
            
        Returns:
            ProcessedDocument: Processed document with chunks and metadata
        """
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
            
        # Get appropriate loader and splitter
        loader_cls, splitter_cls = self.SUPPORTED_FORMATS.get(
            document_path.suffix.lower(),
            (TextLoader, RecursiveCharacterTextSplitter)
        )
        
        # Load document
        loader = loader_cls(str(document_path))
        docs = loader.load()
        
        # Create text splitter
        splitter = splitter_cls(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )
        
        # Process content and extract metadata
        chunks = []
        full_text = ""
        for doc in docs:
            chunks.extend(splitter.split_text(doc.page_content))
            full_text += doc.page_content + "\n"
            
        # Extract metadata based on file type
        metadata = self._extract_metadata(document_path, docs)
        
        # Generate summary and key points for longer documents
        summary = None
        key_points = None
        if len(full_text.split()) > 100:  # Only summarize longer documents
            try:
                summary = self._generate_summary(full_text)
                key_points = self._extract_key_points(full_text)
            except Exception as e:
                logging.warning(f"Error generating summary: {str(e)}")
                
        return ProcessedDocument(
            chunks=chunks,
            metadata=metadata,
            source_id=f"{document_path.stem}_{metadata.get('version', '1.0')}",
            doc_type=document_path.suffix.lower()[1:],
            summary=summary,
            key_points=key_points
        )
        
    def process_directory(self, directory_path: Path) -> Generator[ProcessedDocument, None, None]:
        """Process all supported documents in a directory
        
        Args:
            directory_path: Path to the directory
            
        Yields:
            ProcessedDocument: Processed documents
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        for file_path in directory_path.rglob("*"):
            if file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    yield self.process_document(file_path)
                except Exception as e:
                    logging.error(f"Error processing {file_path}: {str(e)}")
                    
    def _extract_metadata(self, file_path: Path, docs: List[Any]) -> Dict[str, Any]:
        """Extract metadata based on file type"""
        metadata = {
            "source": str(file_path),
            "format": file_path.suffix.lower()[1:],
            "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "size": file_path.stat().st_size,
        }
        
        # Extract format-specific metadata
        if file_path.suffix.lower() == ".md":
            md_metadata = self._extract_markdown_metadata(docs[0].page_content)
            metadata.update(md_metadata)
        elif file_path.suffix.lower() in [".pdf", ".docx"]:
            doc_metadata = docs[0].metadata
            metadata.update({
                k: v for k, v in doc_metadata.items()
                if k in ["title", "author", "subject", "keywords"]
            })
            
        return metadata
        
    def _generate_summary(self, text: str) -> str:
        """Generate a concise summary of the document"""
        chain = load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            verbose=False
        )
        
        # Split text into chunks for summarization
        chunks = self.default_splitter.split_text(text)
        summary = chain.run(chunks)
        
        return summary.strip()
        
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from the document"""
        prompt = """Extract the main key points from the following text. 
        Return them as a list of concise statements:
        
        Text: {text}
        
        Key Points:"""
        
        response = self.llm.invoke(prompt.format(text=text[:4000]))  # Limit text length
        points = [
            point.strip().strip('•-*')
            for point in response.content.split('\n')
            if point.strip()
        ]
        
        return points

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
        if not self.config.knowledge_base_path.exists():
            raise FileNotFoundError(f"Knowledge base JSON not found: {self.config.knowledge_base_path}")
            
        with open(self.config.knowledge_base_path, 'r', encoding='utf-8') as f:
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
                "source": str(self.config.knowledge_base_path),
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