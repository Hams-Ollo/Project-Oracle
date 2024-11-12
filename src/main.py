#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run app.py / streamlit run frontend/streamlit_app.py
# streamlit run chat_app.py
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