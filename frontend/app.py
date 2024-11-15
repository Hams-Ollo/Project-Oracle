#-------------------------------------------------------------------------------------#
# frontend/app.py
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

"""
Main Streamlit App for Project Oracle - Intelligent Onboarding System.
"""

import os
import streamlit as st
from pathlib import Path
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# Add project root to path
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools, KBConfig
from src.core.workflow import create_chat_workflow

# Path configurations
KB_DIR = Path("knowledge_base")
KB_CONFIG = KBConfig(
    base_dir=KB_DIR,
    json_path=KB_DIR / "knowledge_base.json",
    markdown_dir=KB_DIR / "markdown",
    vectors_dir=KB_DIR / "vectors"
)

def init_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "workflow" not in st.session_state:
        st.session_state["workflow"] = None
    if "knowledge_base" not in st.session_state:
        st.session_state["knowledge_base"] = None
    if "app" not in st.session_state:
        st.session_state["app"] = None

def search_knowledge_base(keyword, kb):
    """Search for keyword within the knowledge base."""
    try:
        # Use enhanced search functionality while maintaining the same return format
        results = kb.search_kb(keyword)
        formatted_results = {}
        
        for result in results:
            topic = result.content_id
            formatted_results[topic] = {
                'content': result.full_content,
                'relevance': result.relevance_score,
                'snippet': result.snippet
            }
        
        return formatted_results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return {}

def display_saved_files(kb):
    """Display saved files with options to view or delete."""
    if not kb.content:
        st.write("No knowledge base data available.")
        return

    # Display topics from knowledge base using enhanced structure
    topics = list(kb.content.keys())
    selected_topic = st.selectbox("Select a topic to view:", topics)
    
    if selected_topic:
        topic_data = kb.content[selected_topic]
        metadata = kb.metadata[selected_topic]
        
        st.markdown(f"## {selected_topic.title()}")
        st.caption(f"Last updated: {metadata.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Display content with enhanced metadata
        with st.expander("Content Details"):
            st.markdown("**Tags:**")
            st.write(", ".join(metadata.tags))
            
            st.markdown("**Content:**")
            if isinstance(topic_data, dict):
                for key, value in topic_data.items():
                    st.markdown(f"### {key.replace('_', ' ').title()}")
                    st.markdown(value)
            else:
                st.markdown(topic_data)
            
            if metadata.references:
                st.markdown("**References:**")
                for ref in metadata.references:
                    st.markdown(f"- {ref}")

def setup_components():
    """Set up LLM, web scraper, and knowledge base components."""
    from src.main import ProjectOracleApp
    
    # Create single app instance
    app = ProjectOracleApp()
    st.session_state["app"] = app
    st.session_state["workflow"] = app.workflow
    st.session_state["knowledge_base"] = app.kb
    
    return app.workflow, app.kb

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
    app = st.session_state["app"]
    workflow = app.workflow
    conversation_history = st.session_state["messages"]
    
    try:
        result = None
        for step in workflow.stream({"messages": conversation_history + [HumanMessage(content=user_input)]}):
            if "__end__" not in step:
                for key in step:
                    if "messages" in step[key]:
                        result = step[key]["messages"][-1].content
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
            app = st.session_state["app"]
            result = app.workflow.get("WebScrape").run(url)
            st.markdown(result)

def knowledge_interface():
    """Knowledge base interface with enhanced search capabilities."""
    st.title("📚 Knowledge Base")
    
    app = st.session_state["app"]
    kb = app.kb
    
    # Create tabs for different functions
    search_tab, browse_tab = st.tabs(["🔍 Search", "📖 Browse"])
    
    with search_tab:
        search_query = st.text_input("Search Knowledge Base:", 
                                   placeholder="Enter keywords to search")
        
        if search_query:
            with st.spinner("Searching..."):
                results = search_knowledge_base(search_query, kb)
                if results:
                    for topic, data in results.items():
                        with st.expander(f"📄 {topic.replace('_', ' ').title()}"):
                            st.markdown(data['snippet'])
                            st.progress(min(data['relevance'], 1.0))
                            if st.button("View Full Content", key=f"view_{topic}"):
                                st.markdown(data['content'])
                else:
                    st.info("No results found")
    
    with browse_tab:
        display_saved_files(kb)

def display_sidebar():
    """Sidebar navigation for the Streamlit app."""
    st.sidebar.title("🔮 Project Oracle Navigation")
    
    # Get app instance for statistics
    app = st.session_state.get("app")
    if app:
        stats = app.stats
        
        st.sidebar.markdown("### 📊 Statistics")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Messages", stats['messages'])
            st.metric("Web Pages", stats['web_pages_scraped'])
        with col2:
            st.metric("KB Queries", stats['kb_queries'])
            # Calculate session duration
            duration = datetime.now() - stats['last_active']
            st.metric("Session", f"{duration.seconds // 60}m")
    
    st.sidebar.markdown("---")
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

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="Project Oracle", page_icon="🔮", layout="wide")

    init_session_state()

    if st.session_state["app"] is None:
        setup_components()

    selected_page = display_sidebar()
    selected_page()

if __name__ == "__main__":
    main()