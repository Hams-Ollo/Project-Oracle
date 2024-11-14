#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run streamlit_app.py / streamlit run frontend/streamlit_app.py / python frontend/gradio_app.py
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

import streamlit as st
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import time
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import streamlit.components.v1 as components

# Add project root to system path
sys.path.append(str(Path(__file__).parent.parent))
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from langchain_openai import ChatOpenAI

# Configure Streamlit page
st.set_page_config(
    page_title="Project Oracle",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Sidebar styling */
    .css-1d391kg {
        padding: 1rem;
    }
    
    /* Agent buttons */
    .stButton>button {
        width: 100%;
        text-align: left;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border: none;
        background-color: transparent;
    }
    
    .stButton>button:hover {
        background-color: rgba(128, 90, 213, 0.1);
    }
    
    .selected-agent {
        background-color: rgba(128, 90, 213, 0.2) !important;
        color: rgb(107, 70, 193) !important;
    }
    
    /* Message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: rgba(128, 90, 213, 0.1);
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: white;
        margin-right: 2rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    /* Input box styling */
    .stTextInput>div>div>input {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'messages': [],
        'current_agent': 'chat',
        'show_tutorial': True,
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
    """Initialize AI components if not already initialized"""
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

def render_sidebar():
    """Render the sidebar with agent selection and stats"""
    with st.sidebar:
        st.title("🔮 Project Oracle")
        
        st.subheader("Agents")
        agents = {
            'chat': {'name': 'Chat Agent', 'icon': '💬', 'color': 'blue'},
            'web': {'name': 'Web Scraper', 'icon': '🌐', 'color': 'green'},
            'knowledge': {'name': 'Knowledge Base', 'icon': '📚', 'color': 'purple'}
        }
        
        for agent_id, agent in agents.items():
            button_class = "selected-agent" if st.session_state.current_agent == agent_id else ""
            if st.button(
                f"{agent['icon']} {agent['name']}", 
                key=f"agent_{agent_id}",
                help=f"Switch to {agent['name']}"
            ):
                st.session_state.current_agent = agent_id
                st.rerun()
        
        # Statistics
        st.markdown("---")
        st.subheader("Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", st.session_state.stats['messages'])
            st.metric("KB Queries", st.session_state.stats['kb_queries'])
        with col2:
            st.metric("Web Pages", st.session_state.stats['web_pages'])
            session_duration = datetime.now() - datetime.fromisoformat(st.session_state.stats['session_start'])
            st.metric("Session", f"{session_duration.seconds // 60}m")

def render_chat_interface():
    """Render the main chat interface"""
    # Tutorial message
    if st.session_state.show_tutorial:
        with st.expander("Welcome to Project Oracle! 👋", expanded=True):
            st.markdown("""
            I can help you with:
            - 💬 Natural conversations
            - 🌐 Web scraping and analysis
            - 📚 Star Wars knowledge base queries
            
            Try asking me something!
            """)
            if st.button("Got it!", key="close_tutorial"):
                st.session_state.show_tutorial = False
                st.rerun()
    
    # Chat messages ("😊" if is_user else "🤖"):
    for msg in st.session_state.messages:
        is_user = isinstance(msg, HumanMessage)
        with st.chat_message("😊" if is_user else "🤖"):
            st.markdown(msg.content)
    
    # Chat input
    if prompt := st.chat_input("Message Project Oracle..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.session_state.stats['messages'] += 1
        
        with st.spinner("Thinking..."):
            response = process_message(prompt)
            st.session_state.messages.append(AIMessage(content=response))
        st.rerun()

def process_message(prompt: str) -> str:
    """Process user message and return response"""
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
    init_session_state()
    initialize_components()
    render_sidebar()
    render_chat_interface()

if __name__ == "__main__":
    main()