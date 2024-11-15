#-------------------------------------------------------------------------------------#
# frontend/streamlit_app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run frontend/streamlit_app.py
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
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from langchain_openai import ChatOpenAI

def load_css(file_name):
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

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'messages': [],
        'current_agent': 'chat',
        'stats': {
            'messages': 0,
            'web_pages': 0,
            'kb_queries': 0,
            'session_start': datetime.now().isoformat()
        },
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
        st.session_state.stats['messages'] += 1
        
        with st.spinner("🤔 Processing..."):
            response = process_message(prompt)
            st.session_state.messages.append(AIMessage(content=response))
        st.rerun()

def web_interface():
    """Web scraping and knowledge integration interface"""
    st.title("🌐 Web Knowledge Integration")
    st.write("Access and analyze web-based resources relevant to your role.")
    
    url = st.text_input("Enter URL to analyze:", placeholder="https://example.com")
    if url and st.button("Analyze"):
        with st.spinner("Analyzing content..."):
            response = st.session_state.workflow.get("WebScrape").run(url)
            st.write(response)
            st.session_state.stats['web_pages'] += 1

def knowledge_interface():
    """Knowledge base query interface"""
    st.title("📚 Knowledge Base")
    st.write("Search our organizational knowledge base.")
    
    query = st.text_input("Search knowledge base:", placeholder="Enter your query")
    if query and st.button("Search"):
        with st.spinner("Searching..."):
            response = st.session_state.workflow.get("Knowledge").run(query)
            st.write(response)
            st.session_state.stats['kb_queries'] += 1

def process_message(prompt: str) -> str:
    """Process messages through the workflow"""
    try:
        result = None
        for step in st.session_state.workflow.stream({
            "messages": [HumanMessage(content=prompt)]
        }):
            if "__end__" not in step:
                for key in step:
                    if 'messages' in step[key]:
                        result = step[key]['messages'][-1].content
        return result if result else "I'm not sure how to help with that."
    except Exception as e:
        return f"I encountered an error: {str(e)}"

def main():
    """Main application entry point"""
    st.set_page_config(page_title="Project Oracle", page_icon="🔮", layout="wide")
    
    # Initialize components
    init_session_state()
    initialize_components()
    
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
    
    # Statistics in sidebar
    st.sidebar.divider()
    st.sidebar.subheader("📊 Statistics")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Messages", st.session_state.stats['messages'])
        st.metric("KB Queries", st.session_state.stats['kb_queries'])
    with col2:
        st.metric("Web Pages", st.session_state.stats['web_pages'])
        session_duration = datetime.now() - datetime.fromisoformat(st.session_state.stats['session_start'])
        st.metric("Session", f"{session_duration.seconds // 60}m")
    
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