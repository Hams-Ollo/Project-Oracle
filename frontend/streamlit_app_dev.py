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
# frontend/streamlit_app_dev.py

"""
Main Streamlit App for Project Oracle - Intelligent Onboarding System.
"""

import os
import streamlit as st
from pathlib import Path
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.config.settings import FIRECRAWL_API_KEY  # Ensure this is imported
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from src.services.kb_config import KBConfig  # Add this import

# Path configurations
KB_DIR = Path("knowledge_base")
KB_CONFIG = KBConfig(
    base_dir=KB_DIR,
    json_path=KB_DIR / "knowledge_base.json",
    markdown_dir=KB_DIR / "markdown",
    vectors_dir=KB_DIR / "vectors"
)

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "workflow" not in st.session_state:
        st.session_state["workflow"] = None
    if "knowledge_base" not in st.session_state:
        st.session_state["knowledge_base"] = None

# Helper functions for the Knowledge Base
def search_knowledge_base(keyword, kb):
    """Search for keyword within the knowledge base."""
    results = {}
    
    # Search through topics and their content
    for topic, topic_data in kb.data.get("topics", {}).items():
        for key, value in topic_data.items():
            content = str(value)
            if keyword.lower() in content.lower():
                if topic not in results:
                    results[topic] = {}
                results[topic][key] = value
    
    return results

def display_saved_files(kb):
    """Display saved files with options to view or delete."""
    if not kb.data:
        st.write("No knowledge base data available.")
        return

    # Display topics from knowledge base
    topics = list(kb.data.get("topics", {}).keys())
    selected_topic = st.selectbox("Select a topic to view:", topics)
    
    if selected_topic:
        topic_data = kb.data["topics"][selected_topic]
        st.markdown(f"## {selected_topic.title()}")
        for key, value in topic_data.items():
            with st.expander(f"{key.replace('_', ' ').title()}"):
                if isinstance(value, dict):
                    st.markdown(f"**{value.get('title', '')}**")
                    st.markdown(value.get('content', ''))
                    if 'key_points' in value:
                        st.markdown("**Key Points:**")
                        for point in value['key_points']:
                            st.markdown(f"- {point}")
                else:
                    st.markdown(value)

# Main application components
def setup_components():
    """Set up LLM, web scraper, and knowledge base components."""
    llm = ChatOpenAI(temperature=0.7)
    scraper = WebScraper(FIRECRAWL_API_KEY)
    scraping_tools = create_scraping_tools(scraper)
    
    # Initialize KB with configuration
    kb = KnowledgeBase(config=KB_CONFIG)
    knowledge_tools = create_knowledge_tools(kb)
    workflow = create_chat_workflow(llm, scraping_tools, knowledge_tools)

    return workflow, kb

def chat_interface():
    """Interactive chat interface for general and task-specific conversations."""
    st.title("💬 Onboarding Assistant")

    for msg in st.session_state.messages:
        is_user = isinstance(msg, HumanMessage)
        with st.chat_message("😊" if is_user else "🤖"):
            st.markdown(msg.content)

    if prompt := st.chat_input("How can I assist you?"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.spinner("Thinking..."):
            result = process_workflow_input(prompt)
            st.session_state.messages.append(AIMessage(content=result))
        st.experimental_rerun()

def process_workflow_input(user_input):
    """Process user input through the workflow."""
    workflow = st.session_state["workflow"]
    conversation_history = st.session_state["messages"]
    conversation_history.append(HumanMessage(content=user_input))

    try:
        result = None
        for step in workflow.stream({"messages": conversation_history}):
            if "__end__" not in step:
                for key in step:
                    if "messages" in step[key]:
                        result = step[key]["messages"][-1].content
                        conversation_history.append(step[key]["messages"][-1])
        return result if result else "I didn't quite understand that. Could you rephrase?"
    except Exception as e:
        return f"Error processing your request: {str(e)}"

def web_interface():
    """Web scraping interface for extracting and saving content."""
    st.title("🌐 Web Knowledge Integration")
    st.write("Access and analyze web-based resources.")

    url = st.text_input("Enter a URL to analyze:", placeholder="https://example.com")
    if st.button("Analyze"):
        with st.spinner("Scraping content..."):
            result = st.session_state["workflow"].get("WebScrape").run(url)
            st.markdown(result)

def knowledge_interface():
    """Enhanced knowledge base interface with search and browsing capabilities."""
    st.title("📚 Knowledge Base")
    
    # Get KB instance
    kb = st.session_state.get("knowledge_base")
    if not kb:
        st.error("Knowledge base not initialized")
        return
        
    # Search interface
    search_query = st.text_input("Search Knowledge Base:", 
                                placeholder="Enter keywords to search")
    
    if search_query:
        with st.spinner("Searching..."):
            results = kb.search(search_query)
            if results:
                for result in results:
                    with st.expander(f"Result from {result['source']}"):
                        st.markdown(result['content'])
                        st.caption(f"Source: {result['citation']}")
                        st.progress(result['score'])
            else:
                st.info("No results found")
    
    # Browse interface
    if st.checkbox("Browse Knowledge Base"):
        st.subheader("Knowledge Base Statistics")
        stats = kb.get_statistics()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Documents", stats['total_documents'])
        with col2:
            st.metric("Last Updated", stats.get('last_updated', 'Never'))
            
        st.subheader("Document Types")
        for doc_type, count in stats['document_types'].items():
            st.metric(doc_type.title(), count)

def display_sidebar():
    """Sidebar navigation for the Streamlit app."""
    st.sidebar.title("🔮 Project Oracle Navigation")
    st.sidebar.markdown("Use the navigation below to explore:")
    pages = {
        "Home": homepage,
        "Chat": chat_interface,
        "Web": web_interface,
        "Knowledge": knowledge_interface,
    }
    selected_page = st.sidebar.radio("Choose a section:", list(pages.keys()))
    return pages[selected_page]

def homepage():
    """Landing page with an overview of the app's features."""
    st.title("🔮 Project Oracle - Intelligent Onboarding System")
    st.write("""
    Welcome to Project Oracle, your AI-powered guide through onboarding.
    Select a feature from the sidebar to begin.
    """)
    st.header("Core Features:")
    st.markdown("""
    - 💬 **Chat with the Assistant**: Get personalized guidance and answers.
    - 🌐 **Web Knowledge Integration**: Extract and analyze web-based resources.
    - 📚 **Knowledge Base**: Search and explore organizational knowledge.
    """)

# Main application entry point
def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Project Oracle", page_icon="🔮", layout="wide")

    init_session_state()

    if st.session_state["workflow"] is None or st.session_state["knowledge_base"] is None:
        setup_components()

    # Sidebar for navigation
    selected_page = display_sidebar()
    selected_page()

if __name__ == "__main__":
    main()

