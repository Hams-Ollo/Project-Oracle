#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run streamlit_app.py / streamlit run frontend/streamlit_app.py
#
# Git Commands:
# 1. Initialize repository -> git init
# 2. Add files to staging -> git add .
# 3. Commit changes -> git commit -m "your message"
# 4. Create new branch -> git checkout -b branch-name
# 5. Switch branches -> git checkout branch-name
# 6. Push to remote -> git push -u origin branch-name
# 7. Pull latest changes -> git pull origin branch-name
# 8. Check status -> git status
# 9. View commit history -> git log
#-------------------------------------------------------------------------------------#

################################################################################
# Imports and Configuration
################################################################################

from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from pathlib import Path

# Use relative imports instead of absolute imports
from config.settings import FIRECRAWL_API_KEY
from services.web_scraper import WebScraper, create_scraping_tools
from services.knowledge_base import KnowledgeBase, create_knowledge_tools, KBConfig
from core.workflow import create_chat_workflow
from interface.chat import run_chat_interface

class ProjectOracleApp:
    """Main application class for Project Oracle"""

    def __init__(self):
        """Initialize the application components"""
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0.7)
        
        # Initialize tools and services
        self.scraper = WebScraper(FIRECRAWL_API_KEY)
        self.scraping_tools = create_scraping_tools(self.scraper)
        
        # Initialize KB with new configuration
        kb_config = KBConfig(base_dir=Path("knowledge_base"))
        self.kb = KnowledgeBase(config=kb_config)
        self.knowledge_tools = create_knowledge_tools(self.kb)
        
        # Initialize workflow with KB support
        self.workflow = create_chat_workflow(
            self.llm,
            self.scraping_tools,
            self.knowledge_tools
        )
        
        # Initialize statistics
        self.stats = {
            'messages': 0,
            'web_pages_scraped': 0,
            'kb_queries': 0,
            'last_active': datetime.now(),
            'sessions': 0
        }

    def search_kb(self, keyword: str):
        """Perform keyword search in the knowledge base"""
        return self.kb.search_documents(keyword)

    def search_kb_by_tag(self, tag: str):
        """Perform tag-based search in the knowledge base"""
        return self.kb.search_by_tag(tag)

    def get_internal_links(self, content: str):
        """Get internal links in a document content"""
        return self.kb.find_internal_links(content)
    
    def get_components(self) -> Dict[str, Any]:
        """Get initialized components for use in different interfaces
        
        Returns:
            Dict[str, Any]: Dictionary containing workflow and other components
        """
        return {
            'workflow': self.workflow,
            'kb': self.kb,
            'scraper': self.scraper,
            'stats': self.stats
        }

################################################################################
# Main Entry Point
################################################################################

if __name__ == "__main__":
    app = ProjectOracleApp()
    # For CLI usage
    run_chat_interface(
        workflow=app.workflow,
        stats_manager=app,
        kb=app.kb
    )
