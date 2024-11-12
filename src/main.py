################################################################################
# Imports and Configuration
################################################################################

from langchain_openai import ChatOpenAI

# Use relative imports instead of absolute imports
from config.settings import FIRECRAWL_API_KEY
from services.web_scraper import WebScraper, create_scraping_tools
from services.knowledge_base import KnowledgeBase, create_knowledge_tools
from core.workflow import create_chat_workflow
from interface.chat import run_chat_interface

################################################################################
# Initial Setup and Configuration
################################################################################

# Initialize LLM (Language Learning Model) with temperature parameter
llm = ChatOpenAI(temperature=0.7)

# Initialize scraper and create tools for web scraping
scraper = WebScraper(FIRECRAWL_API_KEY)
scraping_tools = create_scraping_tools(scraper)

# Initialize knowledge base and create tools for knowledge queries
kb = KnowledgeBase()
knowledge_tools = create_knowledge_tools(kb)

################################################################################
# Main Entry Point
################################################################################

if __name__ == "__main__":
    # Create and initialize the chat workflow
    workflow = create_chat_workflow(llm, scraping_tools, knowledge_tools)
    
    # Run the chat interface
    run_chat_interface(workflow)