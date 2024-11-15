#-------------------------------------------------------------------------------------#
# frontend/app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run frontend/app.py
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
#   streamlit run frontend/app.py

"""
Main Streamlit App for Project Oracle - Intelligent Onboarding System.
"""

import os
import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
import logging

# Define paths and setup
sys.path.append(str(Path(__file__).parent.parent))
SCRAPED_CONTENT_DIR = Path("scraped_content")
KB_DIR = Path("knowledge_base")

# Helper Functions for File Management
def save_scraped_content(content: str, file_name: str):
    """Save scraped content to markdown file."""
    try:
        SCRAPED_CONTENT_DIR.mkdir(exist_ok=True)
        file_path = SCRAPED_CONTENT_DIR / f"{file_name}.md"
        file_path.write_text(content)
        st.success(f"Content saved as {file_name}.md")
    except Exception as e:
        st.error(f"Error saving content: {str(e)}")
        logging.error(f"Error saving scraped content: {str(e)}")

def display_saved_files():
    """List saved files with options to view or delete."""
    try:
        SCRAPED_CONTENT_DIR.mkdir(exist_ok=True)
        files = list(SCRAPED_CONTENT_DIR.glob("*.md"))
        
        if not files:
            st.write("No files available.")
            return

        file_names = [f.name for f in files]
        selected_file = st.selectbox("Select a file to view or delete:", file_names)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("View File"):
                file_path = SCRAPED_CONTENT_DIR / selected_file
                content = file_path.read_text()
                st.markdown(content, unsafe_allow_html=True)
        
        with col2:
            if st.button("Delete File"):
                file_path = SCRAPED_CONTENT_DIR / selected_file
                file_path.unlink()
                st.warning(f"{selected_file} deleted.")
                st.experimental_rerun()
        
        with col3:
            if st.button("Clear All"):
                for file in files:
                    file.unlink()
                st.warning("All files cleared.")
                st.experimental_rerun()
                
    except Exception as e:
        st.error(f"Error managing files: {str(e)}")
        logging.error(f"Error in display_saved_files: {str(e)}")

# Session Stats Management
class SessionStats:
    def __init__(self):
        self.initialize_stats()
    
    def initialize_stats(self):
        if 'stats' not in st.session_state:
            st.session_state.stats = {
                'messages': 0,
                'web_pages': 0,
                'kb_queries': 0,
                'session_start': datetime.now(),
                'agent_usage': {
                    'onboarding': 0,
                    'web': 0,
                    'knowledge': 0
                },
                'successful_queries': 0,
                'failed_queries': 0,
                'total_session_time': timedelta(),
                'last_activity': datetime.now()
            }
    
    @staticmethod
    def increment_stat(stat_name: str):
        if stat_name in st.session_state.stats:
            st.session_state.stats[stat_name] += 1
            st.session_state.stats['last_activity'] = datetime.now()
    
    @staticmethod
    def get_session_duration() -> str:
        start_time = st.session_state.stats['session_start']
        duration = datetime.now() - start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    
    @staticmethod
    def track_agent_usage(agent_name: str):
        st.session_state.stats['agent_usage'][agent_name] = \
            st.session_state.stats['agent_usage'].get(agent_name, 0) + 1
    
    @staticmethod
    def update_session_time():
        current_time = datetime.now()
        time_diff = current_time - st.session_state.stats['last_activity']
        st.session_state.stats['total_session_time'] += time_diff
        st.session_state.stats['last_activity'] = current_time

# Load Custom CSS
def load_css(file_name: str):
    with open(file_name) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize Components
def init_session_state():
    defaults = {
        'messages': [],
        'current_agent': 'chat',
        'workflow': None,
        'kb': None
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def initialize_components():
    """Initialize application components with error handling."""
    try:
        if st.session_state.workflow is None:
            llm = ChatOpenAI(temperature=0.7)
            scraper = WebScraper(FIRECRAWL_API_KEY)
            scraping_tools = create_scraping_tools(scraper)
            kb = KnowledgeBase()
            knowledge_tools = create_knowledge_tools(kb)
            
            st.session_state.workflow = create_chat_workflow(
                llm, 
                scraping_tools, 
                knowledge_tools
            )
            st.session_state.kb = kb
            logging.info("Components initialized successfully")
    except Exception as e:
        st.error("Failed to initialize components. Please check your configuration.")
        logging.error(f"Component initialization error: {str(e)}")

# Process Message with Workflow
def process_message(prompt: str) -> str:
    try:
        SessionStats.increment_stat('messages')
        result = None
        for step in st.session_state.workflow.stream({
            "messages": [HumanMessage(content=prompt)]
        }):
            if "__end__" not in step:
                for key in step:
                    if 'messages' in step[key]:
                        result = step[key]['messages'][-1].content
                        if 'WebScrape' in step:
                            SessionStats.increment_stat('web_pages')
                            SessionStats.track_agent_usage('web')
                        elif 'Knowledge' in step:
                            SessionStats.increment_stat('kb_queries')
                            SessionStats.track_agent_usage('knowledge')
                        SessionStats.increment_stat('successful_queries')
        return result if result else "I'm not sure how to help with that."
    except Exception as e:
        SessionStats.increment_stat('failed_queries')
        return f"I encountered an error: {str(e)}"

# Interface Components
def homepage():
    st.title("🔮 Project Oracle - Intelligent Onboarding System 🤖")
    st.write("Welcome to Project Oracle! Your AI-powered guide through the onboarding process. Select a feature from the sidebar to get started.")
    st.divider()
    st.header("Core Features")
    st.subheader("💬 Onboarding Assistant")
    st.write("Personalized guidance, learning paths, and support.")
    st.subheader("🌐 Web Knowledge Integration")
    st.write("Access web-based resources, save documentation, extract information.")
    st.subheader("📚 Knowledge Base")
    st.write("Access organizational knowledge, find documentation, learn about processes.")
    st.divider()

def display_statistics():
    st.sidebar.divider()
    st.sidebar.subheader("📊 Statistics")
    SessionStats.update_session_time()
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("💬 Messages", st.session_state.stats['messages'])
        st.metric("⏱️ Session", SessionStats.get_session_duration())
    with col2:
        st.metric("🌐 Web Pages", st.session_state.stats['web_pages'])
        st.metric("📚 KB Queries", st.session_state.stats['kb_queries'])
    with st.sidebar.expander("Detailed Statistics"):
        st.write("Agent Usage:")
        for agent, count in st.session_state.stats['agent_usage'].items():
            st.write(f"- {agent.title()}: {count}")
        total_queries = (st.session_state.stats['successful_queries'] + 
                         st.session_state.stats['failed_queries'])
        success_rate = (st.session_state.stats['successful_queries'] / total_queries * 100) if total_queries > 0 else 0
        st.write(f"Query Success Rate: {success_rate:.1f}%")
        st.write(f"Total Session Time: {st.session_state.stats['total_session_time']}")

def chat_interface():
    st.title("💬 Onboarding Assistant")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            is_user = isinstance(msg, HumanMessage)
            with st.chat_message("😊" if is_user else "🤖"):
                st.markdown(msg.content)
    if prompt := st.chat_input("How can I help with your onboarding?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.spinner("🤔 Processing..."):
            response = process_message(prompt)
            st.session_state.messages.append(AIMessage(content=response))
        st.rerun()

def web_interface():
    """Web scraping and knowledge integration interface."""
    st.title("🌐 Web Knowledge Integration")
    tab1, tab2 = st.tabs(["Scrape Web Content", "View Saved Content"])

    with tab1:
        st.write("Enter a URL to analyze and save the content as markdown.")
        url = st.text_input("URL:", placeholder="https://example.com")
        
        if st.button("Scrape and Save"):
            with st.spinner("Scraping content..."):
                try:
                    # Use the actual WebScraper instead of simulation
                    scraper = WebScraper(FIRECRAWL_API_KEY)
                    content = scraper.scrape_url(url)
                    
                    if content:
                        file_name = url.replace("https://", "").replace("/", "_")[:50]
                        save_scraped_content(content, file_name)
                        SessionStats.increment_stat('web_pages')
                        SessionStats.track_agent_usage('web')
                    else:
                        st.error("No content retrieved from URL.")
                except Exception as e:
                    st.error(f"Failed to scrape content: {str(e)}")
                    logging.error(f"Scraping error for URL {url}: {str(e)}")

    with tab2:
        st.write("View or manage saved content.")
        display_saved_files()

def knowledge_interface():
    st.title("📚 Knowledge Base")
    st.write("Search our organizational knowledge base.")
    query = st.text_input("Search knowledge base:", placeholder="Enter your query")
    if query and st.button("Search"):
        with st.spinner("Searching..."):
            response = st.session_state.workflow.get("Knowledge").run(query)
            if response and "No information found" not in response:
                SessionStats.increment_stat('kb_queries')
                SessionStats.track_agent_usage('knowledge')
                SessionStats.increment_stat('successful_queries')
            else:
                SessionStats.increment_stat('failed_queries')
            st.write(response)

def main():
    st.set_page_config(page_title="Project Oracle", page_icon="🔮", layout="wide")
    init_session_state()
    initialize_components()
    stats_manager = SessionStats()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button("🏠 Home"):
        st.session_state.page = "Home"
    st.sidebar.subheader("Features")
    if st.sidebar.button("💬 Onboarding Assistant"):
        st.session_state.page = "Chat"
    if st.sidebar.button("🌐 Web Knowledge"):
        st.session_state.page = "Web"
    if st.sidebar.button("📚 Knowledge Base"):
        st.session_state.page = "Knowledge"
    display_statistics()

    # Display Selected Page
    if "page" not in st.session_state:
        st.session_state.page = "Home"
    if st.session_state.page == "Home":
        homepage()
    elif st.session_state.page == "Chat":
        chat_interface()
    elif st.session_state.page == "Web":
        web_interface()
    elif st.session_state.page == "Knowledge":
        knowledge_interface()

if __name__ == "__main__":
    main()
