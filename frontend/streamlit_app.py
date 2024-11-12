#-------------------------------------------------------------------------------------#
# Streamlit Frontend
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
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow

# Page configuration
st.set_page_config(page_title="Project Oracle", page_icon="✨")

# Custom CSS with improved dark theme styling
st.markdown(
    """
    <style>
    /* Main container background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* User message styling */
    .user-message {
        background-color: #2E7DAF;
        color: white;
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 10px;
        text-align: right;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Assistant message styling */
    .agent-message {
        background-color: #1F2937;
        color: #E5E7EB;
        padding: 12px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 75%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    /* Improve header visibility */
    h1 {
        color: #E5E7EB !important;
    }

    /* Improve divider visibility */
    hr {
        border-color: #374151 !important;
    }

    /* Style chat input */
    .stTextInput > div > div > input {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "workflow" not in st.session_state:
    # Initialize components
    llm = ChatOpenAI(temperature=0.7)
    scraper = WebScraper(FIRECRAWL_API_KEY)
    scraping_tools = create_scraping_tools(scraper)
    kb = KnowledgeBase()
    knowledge_tools = create_knowledge_tools(kb)
    
    # Create workflow
    st.session_state.workflow = create_chat_workflow(llm, scraping_tools, knowledge_tools)

# Display header
st.title("✨ Project Oracle")
st.divider()

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'''<div class="user-message">{message["content"]}</div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div class="agent-message">{message["content"]}</div>''', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
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
        
        # Rerun to update display
        st.rerun()
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.rerun() 