#-------------------------------------------------------------------------------------#
# frontend/streamlit_app_dev.py
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
Main Streamlit App for Project Oracle - Advanced Knowledge Management System
"""

import os
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import plotly.graph_objects as go
import plotly.express as px
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import pandas as pd
import networkx as nx
import logging
from pydantic.v1 import BaseModel

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.services.advanced_search import AdvancedSearch
from src.services.knowledge_graph import KnowledgeGraph
from src.services.kb_config import KBConfig
from src.core.workflow import create_chat_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('project_oracle.log')
    ]
)

# Define paths and setup
ROOT_DIR = Path(__file__).parent.parent
SCRAPED_CONTENT_DIR = ROOT_DIR / "scraped_content"
KB_DIR = ROOT_DIR / "knowledge_base"
UPLOAD_DIR = ROOT_DIR / "uploads"
VECTORS_DIR = KB_DIR / "vectors"
DOCS_DIR = KB_DIR / "docs"
GRAPH_DIR = KB_DIR / "graph"
VECTOR_STORE_DIR = KB_DIR / "vector_store"

# Ensure directories exist
for dir_path in [SCRAPED_CONTENT_DIR, KB_DIR, UPLOAD_DIR, VECTORS_DIR, DOCS_DIR, GRAPH_DIR, VECTOR_STORE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Load Custom CSS
def load_css():
    st.markdown("""
        <style>
        /* Dark theme */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E;
            padding: 1rem;
        }
        .stButton button {
            background-color: #2E2E2E;
            color: #FFFFFF;
            border: 1px solid #3E3E3E;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            width: 100%;
            margin-bottom: 0.5rem;
        }
        .stButton button:hover {
            background-color: #3E3E3E;
            border-color: #4E4E4E;
        }
        .css-1d391kg, .css-1p05t8e {
            background-color: #1E1E1E;
        }
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: #2E2E2E;
            color: #FFFFFF;
            border-color: #3E3E3E;
        }
        h1, h2, h3, p {
            color: #FFFFFF;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 0.5rem;
        }
        .user-message {
            background-color: #2E2E2E;
        }
        .bot-message {
            background-color: #3E3E3E;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize Session State
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'stats' not in st.session_state:
        st.session_state.stats = SessionStats()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0
    if 'kb' not in st.session_state:
        try:
            kb_config = KBConfig(
                base_dir=str(KB_DIR),
                vector_store_path=str(VECTOR_STORE_DIR),
                knowledge_base_path=str(KB_DIR / "knowledge_base.json")
            )
            kb = KnowledgeBase(kb_config)
            st.session_state.kb = kb
            st.session_state.search = AdvancedSearch(kb)
        except Exception as e:
            st.error(f"Error initializing knowledge base: {str(e)}")
            logging.error(f"Error initializing knowledge base: {str(e)}")

# Helper Functions for File Management
def save_uploaded_file(uploaded_file) -> Optional[Path]:
    """Save uploaded file and return its path."""
    try:
        file_path = UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        logging.error(f"File upload error: {str(e)}")
        return None

def process_document(kb: KnowledgeBase, file_path: Path) -> bool:
    """Process document and add to knowledge base."""
    try:
        # Process the document
        processed_doc = kb.doc_processor.process_document(file_path)
        
        # Add document chunks to vector store
        chunk_ids = kb.vector_store.add_document(processed_doc)
        
        # Update source map
        kb._update_source_map(processed_doc, chunk_ids)
        
        return True
    except Exception as e:
        logging.error(f"Document processing error: {str(e)}", exc_info=True)
        return False

# Session Stats Management
class SessionStats:
    def __init__(self):
        self.initialize_stats()
    
    def initialize_stats(self):
        """Initialize session statistics."""
        self.session_start = datetime.now()
        self.messages = 0
        self.documents_processed = 0
        self.searches_performed = 0
        self.agent_usage = {
            'search': 0,
            'process': 0,
            'analyze': 0
        }
        self.document_types = {}
        self.search_terms = []
    
    def update_stats(self, stat_type: str, value: any = 1):
        if hasattr(self, stat_type):
            if isinstance(getattr(self, stat_type), int):
                setattr(self, stat_type, getattr(self, stat_type) + value)
            elif isinstance(getattr(self, stat_type), list):
                getattr(self, stat_type).append(value)
            elif isinstance(getattr(self, stat_type), dict):
                if value in getattr(self, stat_type):
                    getattr(self, stat_type)[value] += 1
                else:
                    getattr(self, stat_type)[value] = 1

# Interface Components
def homepage():
    st.title("Project Oracle - Advanced Knowledge Management")
    st.markdown("""
    Welcome to Project Oracle, your intelligent knowledge management system that transforms how you store, search, and understand your documents.
    
    ### Features:
    
    #### 📚 Document Management
    Upload and organize your documents with ease. Supports multiple formats including PDF, Word, text files, and more. 
    Our system automatically processes and indexes your documents for advanced search and analysis.
    
    #### 🔍 Advanced Search
    Go beyond simple keyword matching with our AI-powered semantic search. Find relevant information even when 
    the exact terms don't match, thanks to our advanced natural language processing capabilities.
    
    #### 🕸️ Knowledge Graph
    Visualize connections between your documents and concepts. Our system automatically builds an interactive 
    knowledge graph that reveals hidden relationships and patterns in your document collection.
    
    #### 📊 Analytics Dashboard
    Gain insights into your document collection with powerful analytics. Track key metrics, identify trends, 
    and understand the composition of your knowledge base through intuitive visualizations.
    
    #### 🌐 Web Integration
    Seamlessly integrate with web sources to enrich your knowledge base. Import content from websites and 
    keep your information up-to-date with our web crawling capabilities.
    
    #### 💬 Chat Interface
    Engage with Project Oracle using natural language. Ask questions, request information, or simply chat with 
    our AI assistant to get the most out of your knowledge base.
    
    Select a feature from the sidebar to get started.
    """)

def chat_interface():
    st.header("Chat Interface")
    
    # Initialize chat components if not already done
    if 'workflow' not in st.session_state:
        try:
            llm = ChatOpenAI(temperature=0.7)
            scraper = WebScraper(FIRECRAWL_API_KEY)
            scraping_tools = create_scraping_tools(scraper)
            knowledge_tools = create_knowledge_tools(st.session_state.kb)
            
            st.session_state.workflow = create_chat_workflow(
                llm, 
                scraping_tools, 
                knowledge_tools
            )
        except Exception as e:
            st.error(f"Failed to initialize chat components: {str(e)}")
            logging.error(f"Chat initialization error: {str(e)}")
            return
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">🤖: {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Ask me anything...", key=f"chat_input_{st.session_state.chat_input_key}")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Process message through workflow
            messages = [HumanMessage(content=user_input)]
            response = None
            
            for step in st.session_state.workflow.stream({"messages": messages}):
                if "__end__" not in step:
                    for key in step:
                        if 'messages' in step[key]:
                            response = step[key]['messages'][-1].content
            
            if response:
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.session_state.stats.update_stats('messages')
            else:
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": "I apologize, but I couldn't process your request. Please try again."
                })
                
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            logging.error(f"Chat processing error: {str(e)}")
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": "I encountered an error processing your request. Please try again."
            })
        
        # Increment key to clear input
        st.session_state.chat_input_key += 1
        st.rerun()

def document_management_interface(kb: KnowledgeBase):
    st.header("Document Management")
    
    # Upload section
    uploaded_files = st.file_uploader(
        "Upload Documents", 
        type=['txt', 'pdf', 'json', 'md', 'markdown'],
        accept_multiple_files=True,
        help="Upload one or more documents to add to your knowledge base. Supported formats: TXT, PDF, JSON, Markdown"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                file_path = save_uploaded_file(uploaded_file)
                if file_path:
                    if process_document(kb, file_path):
                        st.success(f"✅ Successfully processed: {uploaded_file.name}")
                        st.session_state.stats.update_stats('documents_processed')
                    else:
                        st.error(f"❌ Failed to process: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                logging.error(f"Document processing error for {uploaded_file.name}: {str(e)}", exc_info=True)
    
    # Document list
    st.subheader("Processed Documents")
    try:
        # Get unique documents from source map
        documents = []
        unique_sources = set()
        
        for chunk_id, metadata in kb.source_map.items():
            source = metadata["source"]
            if source not in unique_sources:
                documents.append({
                    "title": Path(source).stem,
                    "source": source,
                    "type": metadata["type"],
                    "doc_type": metadata["doc_type"],
                    "processed_at": metadata["processed_at"]
                })
                unique_sources.add(source)
        
        # Sort by processing date
        documents = sorted(documents, key=lambda x: x["processed_at"], reverse=True)
        
        if not documents:
            st.info("No documents have been processed yet. Upload documents to get started.")
        else:
            for doc in documents:
                with st.expander(f"📄 {doc['title']}"):
                    st.write(f"**Source:** {doc['source']}")
                    st.write(f"**Type:** {doc['type']}")
                    st.write(f"**Document Type:** {doc['doc_type']}")
                    st.write(f"**Processed:** {doc['processed_at']}")
    except Exception as e:
        st.error(f"Error listing documents: {str(e)}")
        logging.error(f"Error in document listing: {str(e)}", exc_info=True)

def advanced_search_interface(kb: KnowledgeBase, search: AdvancedSearch):
    st.header("Advanced Search")
    
    # Search Configuration
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter your search query")
    with col2:
        search_type = st.selectbox("Search Type", ["Semantic", "Keyword", "Hybrid"])
    
    # Filters
    with st.expander("Search Filters"):
        date_range = st.date_input("Date Range", [])
        doc_types = st.multiselect("Document Types", list(st.session_state.stats.document_types.keys()))
    
    if query:
        st.session_state.stats.update_stats('searches_performed')
        st.session_state.stats.update_stats('search_terms', query)
        
        results = search.search(
            query=query,
            search_type=search_type.lower(),
            filters={
                'date_range': date_range if date_range else None,
                'doc_types': doc_types if doc_types else None
            }
        )
        
        st.subheader(f"Search Results ({len(results)} found)")
        for result in results:
            with st.expander(result.title):
                st.markdown(result.content)
                st.json(result.metadata)

def knowledge_graph_interface(graph: KnowledgeGraph):
    st.header("Knowledge Graph")
    
    # Graph Controls
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("Search entities")
    with col2:
        depth = st.slider("Graph Depth", 1, 5, 2)
    
    # Generate and display graph
    if search_term:
        nodes, edges = graph.get_subgraph(search_term, depth)
        
        # Create networkx graph
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        
        # Convert to plotly figure
        pos = nx.spring_layout(G)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines'))
        
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', text=list(G.nodes())))
        
        st.plotly_chart(fig)

def analytics_dashboard():
    st.header("Analytics Dashboard")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents Processed", st.session_state.stats.documents_processed)
    with col2:
        st.metric("Searches Performed", st.session_state.stats.searches_performed)
    with col3:
        st.metric("Messages Exchanged", st.session_state.stats.messages)
    
    # Document Type Distribution
    st.subheader("Document Distribution")
    doc_types_df = pd.DataFrame(
        list(st.session_state.stats.document_types.items()),
        columns=['Type', 'Count']
    )
    fig = px.pie(doc_types_df, values='Count', names='Type')
    st.plotly_chart(fig)
    
    # Search Term Analysis
    st.subheader("Popular Search Terms")
    search_terms = pd.Series(st.session_state.stats.search_terms).value_counts()
    if not search_terms.empty:
        fig = px.bar(search_terms)
        st.plotly_chart(fig)

def main():
    # Configure page
    st.set_page_config(
        page_title="Project Oracle",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': " 🔮 Project Oracle - Advanced Knowledge Management System 🤖"
        }
    )
    
    # Initialize
    load_css()
    init_session_state()
    
    # Dark theme
    st.markdown("""
        <style>
        .main {
            background-color: #121212;
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🔮 Project Oracle 🤖")
        
        menu_options = {
            "Home": "🏠",
            "Chat Interface": "💬",
            "Document Management": "📁",
            "Advanced Search": "🔍",
            "Knowledge Graph": "🕸️",
            "Analytics": "📊"
        }
        
        for page, icon in menu_options.items():
            if st.button(f"{icon} {page}"):
                st.session_state.current_page = page
        
        # Session Information
        st.markdown("---")
        st.markdown("### Session Info")
        session_duration = datetime.now() - st.session_state.stats.session_start
        st.text(f"Duration: {str(session_duration).split('.')[0]}")
    
    # Main Content
    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Chat Interface":
        chat_interface()
    elif st.session_state.current_page == "Document Management":
        document_management_interface(st.session_state.kb)
    elif st.session_state.current_page == "Advanced Search":
        advanced_search_interface(st.session_state.kb, st.session_state.search)
    elif st.session_state.current_page == "Knowledge Graph":
        knowledge_graph_interface(st.session_state.kb.knowledge_graph)
    elif st.session_state.current_page == "Analytics":
        analytics_dashboard()

if __name__ == "__main__":
    main()
