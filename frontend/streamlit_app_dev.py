#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run streamlit_app.py / streamlit run frontend/streamlit_app_dev.py
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
import base64

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

# Function to add background image
def add_background(image_file):
    with open(image_file, "rb") as image:
        encoded_image = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add background image
add_background('static/background.jpg')  # Replace with your image path

# Custom CSS for styling
st.markdown("""
<style>
/* Hide default Streamlit header and footer */
header, footer {visibility: hidden;}

/* Main app styling */
.stApp {
    background-color: rgba(0, 0, 0, 0);
}

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
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    max-width: 70%;
}

.user-message {
    background-color: #DCF8C6;
    align-self: flex-end;
}

.assistant-message {
    background-color: #FFFFFF;
    align-self: flex-start;
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-right: 10px;
}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
}

/* Input box styling */
.stTextInput>div>div>input {
    border-radius: 0.5rem;
}

/* Button styling */
.custom-button {
    background-color: #8E44AD;
    color: #FFFFFF;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
}

.custom-button:hover {
    background-color: #732d91;
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'messages': [],
        'current_agent': 'Chat Agent',
        'show_tutorial': True,
        'stats': {
            'messages': 0,
            'web_pages': 0,
            'kb_queries': 0,
            'session_start': datetime.now().isoformat()
        },
        'workflow': None,
        'kb': None,
        'avatars': {
            'user': 'static/user_avatar.png',        # Replace with your avatar image path
            'assistant': 'static/assistant_avatar.png'  # Replace with your avatar image path
        }
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
        st.image('static/logo.png', use_column_width=True)  # Replace with your logo image path
        st.title("🔮 Project Oracle")

        st.subheader("Agents")
        agents = ['Chat Agent', 'Web Scraper', 'Knowledge Base']

        selected_agent = st.radio(
            "Select Agent",
            agents,
            index=agents.index(st.session_state.current_agent)
        )
        st.session_state.current_agent = selected_agent

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
    """Render the chat interface with customized message bubbles and avatars"""
    st.header("💬 Chat with Project Oracle")

    chat_container = st.container()
    with chat_container:
        if st.session_state.show_tutorial:
            with st.expander("Welcome to Project Oracle! 👋", expanded=True):
                st.markdown("""
                **I can help you with:**
                - 💬 Natural conversations
                - 🌐 Web scraping and analysis
                - 📚 Knowledge base queries

                **Try asking me something!**
                """)
                if st.button("Got it!", key="close_tutorial"):
                    st.session_state.show_tutorial = False
                    st.experimental_rerun()

        # Display chat messages
        for msg in st.session_state.messages:
            is_user = isinstance(msg, HumanMessage)
            avatar_img = st.session_state.avatars['user'] if is_user else st.session_state.avatars['assistant']
            alignment = 'flex-end' if is_user else 'flex-start'
            message_class = 'user-message' if is_user else 'assistant-message'

            message_container = f"""
            <div style='display: flex; align-items: flex-start; justify-content: {alignment};'>
                {'<img src="data:image/png;base64,{}" class="message-avatar">'.format(get_base64_image(avatar_img)) if avatar_img else ''}
                <div class='chat-message {message_class}'>{msg.content}</div>
            </div>
            """
            st.markdown(message_container, unsafe_allow_html=True)

        # Chat input
        prompt = st.text_input("Type your message...", key="user_input", placeholder="Ask me anything...")
        if prompt:
            st.session_state.messages.append(HumanMessage(content=prompt))
            st.session_state.stats['messages'] += 1

            with st.spinner("Thinking..."):
                response = process_message(prompt)
                st.session_state.messages.append(AIMessage(content=response))
            st.experimental_rerun()

def render_web_scraper_interface():
    """Render the web scraper interface"""
    st.header("🌐 Web Scraper")
    url = st.text_input("Enter URL to scrape:")
    if url:
        with st.spinner("Scraping the web page..."):
            content = st.session_state.scraper.scrape(url)
            st.session_state.stats['web_pages'] += 1
            st.success("Scraping completed!")
            st.text_area("Scraped Content:", content, height=300)

def render_knowledge_base_interface():
    """Render the knowledge base interface"""
    st.header("📚 Knowledge Base")
    query = st.text_input("Search the knowledge base:")
    if query:
        with st.spinner("Searching the knowledge base..."):
            response = st.session_state.kb.query(query)
            st.session_state.stats['kb_queries'] += 1
            st.write("**Results:**")
            st.write(response)

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

def get_base64_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def main():
    """Main application entry point"""
    init_session_state()
    initialize_components()
    render_sidebar()

    # Main content area
    if st.session_state.current_agent == 'Chat Agent':
        render_chat_interface()
    elif st.session_state.current_agent == 'Web Scraper':
        render_web_scraper_interface()
    elif st.session_state.current_agent == 'Knowledge Base':
        render_knowledge_base_interface()
    else:
        st.write("Please select an agent from the sidebar.")

if __name__ == "__main__":
    main()
