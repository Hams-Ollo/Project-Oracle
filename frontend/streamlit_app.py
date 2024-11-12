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

import streamlit as st
from pathlib import Path
import sys
from typing import List, Dict
import time
from datetime import datetime

# Add the parent directory to system path to import dev module
sys.path.append(str(Path(__file__).parent))
from dev import create_chat_workflow, HumanMessage, SystemMessage

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'workflow' not in st.session_state:
        st.session_state.workflow = create_chat_workflow()

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