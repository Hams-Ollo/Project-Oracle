import streamlit as st
from pathlib import Path
import sys
from typing import List, Dict
import time
from datetime import datetime

# Add the parent directory to system path to import dev module
sys.path.append(str(Path(__file__).parent))
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'workflow' not in st.session_state:
        # Initialize components
        llm = ChatOpenAI(temperature=0.7)
        scraper = WebScraper(FIRECRAWL_API_KEY)
        scraping_tools = create_scraping_tools(scraper)
        kb = KnowledgeBase()
        knowledge_tools = create_knowledge_tools(kb)
        
        # Create workflow
        st.session_state.workflow = create_chat_workflow(llm, scraping_tools, knowledge_tools)

def display_message(message: Dict, is_user: bool):
    """Display a single message with appropriate styling"""
    with st.chat_message("😊" if is_user else "🔮"):
        st.markdown(message["content"])

def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.messages:
        is_user = message["role"] == "user"
        display_message(message, is_user)

def process_user_input(user_input: str) -> None:
    """Process user input through workflow and generate response"""
    if not user_input:
        return

    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show thinking indicator
    with st.spinner("🤔 Oracle is thinking..."):
        # Process through workflow
        conversation_history = [
            SystemMessage(content="""You are a helpful AI assistant that can:
            1. Engage in natural conversation
            2. Analyze and extract web content when requested
            3. Access and query the knowledge base
            
            Be friendly, helpful, and engaging in your responses.""")
        ]
        
        # Add chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                conversation_history.append(HumanMessage(content=msg["content"]))
        
        # Get response from workflow
        config = {"recursion_limit": 150, "timeout": 300}
        
        try:
            result = None
            for step in st.session_state.workflow.stream({
                "messages": conversation_history
            }, config=config):
                if "__end__" not in step:
                    for key in step:
                        if 'messages' in step[key]:
                            result = step[key]['messages'][-1].content
            
            # Add assistant response to chat
            if result:
                st.session_state.messages.append({"role": "assistant", "content": result})
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

def create_sidebar():
    """Create the sidebar with information and controls"""
    with st.sidebar:
        st.title("🔮 Project Oracle")
        st.markdown("""
        ### Capabilities:
        - 💭 Natural Conversation
        - 🌐 Web Scraping
        - 📚 Knowledge Base Queries
        
        ### Available Features:
        1. General chat and conversation
        2. Web content extraction and storage
        3. Star Wars knowledge base queries
        
        ### Example Commands:
        - "Tell me about the Jedi Order"
        - "Scrape https://example.com"
        - "What topics do you know about?"
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Project Oracle",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Main chat container
    st.title("🔮 Project Oracle")
    st.markdown("Your gateway to knowledge and web content")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    user_input = st.chat_input("Message Project Oracle...")
    if user_input:
        process_user_input(user_input)
        st.rerun()

if __name__ == "__main__":
    main()