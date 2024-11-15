#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run frontend/streamlit_app_dev.py
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

"""
Main Streamlit App functionality for Project Oracle's Intelligent Onboarding System.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from langchain_openai import ChatOpenAI

class SessionStats:
    """
    Manages session statistics tracking for Project Oracle
    """
    def __init__(self):
        self.initialize_stats()
    
    def initialize_stats(self):
        """Initialize or reset session statistics"""
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
        """Increment a specific statistic"""
        if stat_name in st.session_state.stats:
            st.session_state.stats[stat_name] += 1
            st.session_state.stats['last_activity'] = datetime.now()
    
    @staticmethod
    def get_session_duration() -> str:
        """Calculate and format session duration"""
        start_time = st.session_state.stats['session_start']
        duration = datetime.now() - start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    @staticmethod
    def track_agent_usage(agent_name: str):
        """Track which agents are being used"""
        if 'agent_usage' not in st.session_state.stats:
            st.session_state.stats['agent_usage'] = {}
        st.session_state.stats['agent_usage'][agent_name] = \
            st.session_state.stats['agent_usage'].get(agent_name, 0) + 1
    
    @staticmethod
    def update_session_time():
        """Update total session time based on last activity"""
        if 'last_activity' in st.session_state.stats:
            current_time = datetime.now()
            time_diff = current_time - st.session_state.stats['last_activity']
            st.session_state.stats['total_session_time'] += time_diff
            st.session_state.stats['last_activity'] = current_time

def load_css(file_name: str):
    """Load custom CSS styling"""
    with open(file_name) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def homepage():
    """Project Oracle homepage with overview of features"""
    st.title("🔮 Project Oracle - Intelligent Onboarding System 🤖")
    st.write("Welcome to Project Oracle! Your AI-powered guide through the onboarding process. \
             Select a feature from the sidebar to get started.")
    
    st.divider()
    st.header("Core Features")
    st.write("")
    
    st.subheader("💬 Onboarding Assistant")
    st.write("- Personalized guidance through your onboarding journey")
    st.write("- Custom learning paths based on your role and experience")
    st.write("- Real-time support and answers to your questions")
    st.write("")
    
    st.subheader("🌐 Web Knowledge Integration")
    st.write("- Access and analyze web-based resources")
    st.write("- Save and organize important documentation")
    st.write("- Extract relevant information from online sources")
    st.write("")
    
    st.subheader("📚 Knowledge Base")
    st.write("- Access comprehensive organizational knowledge")
    st.write("- Find documentation and best practices")
    st.write("- Learn about teams, projects, and processes")
    st.write("")
    
    st.divider()

def display_statistics():
    """Display enhanced statistics in the sidebar"""
    st.sidebar.divider()
    st.sidebar.subheader("📊 Statistics")
    
    # Update session time
    SessionStats.update_session_time()
    
    # Create three rows of metrics
    col1, col2 = st.sidebar.columns(2)
    
    # Row 1: Message and Session stats
    with col1:
        st.metric("💬 Messages", st.session_state.stats['messages'])
        st.metric("⏱️ Session", SessionStats.get_session_duration())
    
    # Row 2: Web and KB stats
    with col2:
        st.metric("🌐 Web Pages", st.session_state.stats['web_pages'])
        st.metric("📚 KB Queries", st.session_state.stats['kb_queries'])
    
    # Detailed statistics in expander
    with st.sidebar.expander("Detailed Statistics"):
        st.write("Agent Usage:")
        for agent, count in st.session_state.stats['agent_usage'].items():
            st.write(f"- {agent.title()}: {count}")
        
        total_queries = (st.session_state.stats['successful_queries'] + 
                        st.session_state.stats['failed_queries'])
        success_rate = 0
        if total_queries > 0:
            success_rate = (st.session_state.stats['successful_queries'] / 
                          total_queries) * 100
        
        st.write(f"Query Success Rate: {success_rate:.1f}%")
        st.write(f"Total Session Time: {st.session_state.stats['total_session_time']}")

def init_session_state():
    """Initialize session state variables"""
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
    """Initialize AI components and tools"""
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

def process_message(prompt: str) -> str:
    """Process messages through the workflow with enhanced statistics tracking"""
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
                        
                        # Track which agent handled the request
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

def chat_interface():
    """Main chat interface for the Onboarding Assistant"""
    st.title("💬 Onboarding Assistant")
    
    # Chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            is_user = isinstance(msg, HumanMessage)
            with st.chat_message("😊" if is_user else "🤖"):
                st.markdown(msg.content)
    
    # Chat input
    if prompt := st.chat_input("How can I help with your onboarding?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        with st.spinner("🤔 Processing..."):
            response = process_message(prompt)
            st.session_state.messages.append(AIMessage(content=response))
        st.rerun()

def web_interface():
    """Web scraping interface with statistics tracking"""
    st.title("🌐 Web Knowledge Integration")
    st.write("Access and analyze web-based resources relevant to your role.")
    
    url = st.text_input("Enter URL to analyze:", placeholder="https://example.com")
    if url and st.button("Analyze"):
        with st.spinner("Analyzing content..."):
            response = st.session_state.workflow.get("WebScrape").run(url)
            if response and "Successfully scraped" in response:
                SessionStats.increment_stat('web_pages')
                SessionStats.track_agent_usage('web')
                SessionStats.increment_stat('successful_queries')
            else:
                SessionStats.increment_stat('failed_queries')
            st.write(response)

def knowledge_interface():
    """Knowledge base interface with statistics tracking"""
    st.title("📚 Knowledge Base")
    st.write("Search our organizational knowledge base.")
    
    query = st.text_input("Search knowledge base:", placeholder="Enter your query")
    if query and st.button("Search"):
        with st.spinner("Searching..."):
            response = st.session_state.workflow.get("Knowledge").run(query)
            if response and not "No information found" in response:
                SessionStats.increment_stat('kb_queries')
                SessionStats.track_agent_usage('knowledge')
                SessionStats.increment_stat('successful_queries')
            else:
                SessionStats.increment_stat('failed_queries')
            st.write(response)

def main():
    """Main application entry point"""
    st.set_page_config(page_title="Project Oracle", page_icon="🔮", layout="wide")
    
    # Initialize components
    init_session_state()
    initialize_components()
    stats_manager = SessionStats()
    
    # Sidebar navigation
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
    
    # Display statistics
    display_statistics()
    
    # Display selected page
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