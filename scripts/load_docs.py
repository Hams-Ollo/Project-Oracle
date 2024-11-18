"""Script to load documents from docs folder into knowledge base"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.services.knowledge_base import KnowledgeBase, KBConfig

def load_docs():
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to the .env file:")
        print('OPENAI_API_KEY="your-api-key-here"')
        return
    
    # Initialize knowledge base with configuration
    kb_config = KBConfig(base_dir=Path("knowledge_base"))
    kb = KnowledgeBase(config=kb_config)
    
    # Get all markdown files from docs directory
    docs_dir = Path("docs")
    markdown_files = list(docs_dir.glob("*.md"))
    txt_files = list(docs_dir.glob("*.txt"))
    
    # Add each document to knowledge base
    for doc_file in markdown_files + txt_files:
        print(f"Adding document: {doc_file}")
        success = kb.add_document(str(doc_file))
        if success:
            print(f"Successfully added {doc_file}")
        else:
            print(f"Failed to add {doc_file}")
    
    # List all documents to verify
    print("\nDocuments in knowledge base:")
    documents = kb.list_documents()
    for doc in documents:
        print(f"- {doc['title']} ({doc['doc_type']})")

if __name__ == "__main__":
    load_docs()
