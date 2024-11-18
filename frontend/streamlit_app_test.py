#-------------------------------------------------------------------------------------#
# frontend/streamlit_app_test.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run frontend/streamlit_app_test.py
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
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
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
                base_dir=KB_DIR,
                vector_store_path=VECTOR_STORE_DIR,
                markdown_dir=DOCS_DIR,
                vectors_dir=VECTORS_DIR,
                graph_dir=GRAPH_DIR,
                knowledge_base_path=KB_DIR / "knowledge_base.json"
            )
            kb = KnowledgeBase(config=kb_config)
            st.session_state.kb = kb
            st.session_state.search = AdvancedSearch(kb=kb)
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
        self.documents_processed = 0
        self.queries_made = 0
        self.chat_messages = 0
        self.document_types = {}
        self.last_update = datetime.now()
        self.session_start = datetime.now()
        self.searches_performed = 0
        self.total_tokens = 0
        self.error_count = 0
        self.search_terms = []  # Added search terms list
        
    def update_stats(self, stat_type: str, value: int = 1):
        """Update session statistics."""
        if hasattr(self, stat_type):
            current_value = getattr(self, stat_type)
            if isinstance(current_value, dict):
                current_value['total'] = current_value.get('total', 0) + value
            elif isinstance(current_value, list):
                if isinstance(value, str):
                    current_value.append(value)
            else:
                setattr(self, stat_type, current_value + value)
        self.last_update = datetime.now()
        
    def update_document_types(self, doc_type: str):
        """Update document type statistics."""
        if doc_type not in self.document_types:
            self.document_types[doc_type] = 0
        self.document_types[doc_type] += 1
        
    def get_session_duration(self) -> timedelta:
        """Get the current session duration."""
        return datetime.now() - self.session_start

# Interface Components
def homepage():
    st.title("Project Oracle - Advanced Knowledge Base Management and Onboarding Assistant")
    
    st.markdown("""
    Welcome to Project Oracle, your intelligent knowledge management system that transforms how you store, search, and understand your documents. 
    Additionally, Project Oracle is a multi-agent onboarding assistant solution that assists and guides the user with learning, onboarding, and guidance as they navigate the custom knowledge base of data which the system has access to. 
    Our system automatically processes and indexes your documents for advanced search and analysis. 
    It also provides AI-powered semantic search, knowledge graph visualization, analytics dashboard, web integration and natural language chat interface features.
    
    ### Features:
    
    #### 📚 Document Management
    Upload and organize your documents with ease. Supports multiple formats including PDF, Word, text files, and more. Documents are automatically processed, chunked, and indexed for efficient retrieval.
    
    #### 🤖 AI-Powered Chat Interface
    Engage in natural conversations with your knowledge base. Our AI assistant helps you understand and extract insights from your documents while providing guided onboarding support.
    
    #### 🔍 Advanced Search
    Utilize semantic search capabilities to find relevant information across your entire knowledge base. Combines both keyword and semantic understanding for better results.
    
    #### 📊 Analytics Dashboard
    Track your knowledge base growth, usage patterns, and get insights into your document collection through interactive visualizations.
    
    #### 🕸️ Knowledge Graph
    Visualize relationships between documents and concepts in your knowledge base through an interactive knowledge graph.
    
    #### 🌐 Web Integration
    Seamlessly integrate web content into your knowledge base through our web scraping capabilities.
    
    ### Getting Started:
    1. Upload your documents in the Document Management section
    2. Use the Chat Interface to start interacting with your knowledge base
    3. Explore Advanced Search for specific queries
    4. View relationships in the Knowledge Graph
    5. Monitor usage in the Analytics Dashboard
    """)
    
    # Quick Stats
    if 'stats' in st.session_state:
        st.subheader("📈 Quick Stats")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            docs_processed = st.session_state.stats.documents_processed
            total_docs = docs_processed.get('total', 0) if isinstance(docs_processed, dict) else docs_processed
            st.metric("Documents Processed", total_docs)
        with col2:
            queries = st.session_state.stats.queries_made
            total_queries = queries.get('total', 0) if isinstance(queries, dict) else queries
            st.metric("Queries Made", total_queries)
        with col3:
            messages = st.session_state.stats.chat_messages
            total_messages = messages.get('total', 0) if isinstance(messages, dict) else messages
            st.metric("Chat Messages", total_messages)
            
    # System Status
    st.subheader("⚡ System Status")
    col1, col2 = st.columns(2)
    with col1:
        if 'kb' in st.session_state:
            st.success("✅ Knowledge Base: Connected")
        else:
            st.error("❌ Knowledge Base: Not Connected")
    with col2:
        try:
            import openai
            st.success("✅ OpenAI API: Connected")
        except:
            st.warning("⚠️ OpenAI API: Not Connected")

def chat_interface():
    st.header("🤖 AI Assistant & Knowledge Base Chat")
    
    # Initialize chat components if not already done
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        
    # Chat interface explanation
    st.markdown("""
    Chat with your knowledge base using natural language. Our AI assistant can:
    - Answer questions about your documents
    - Guide you through onboarding processes
    - Explain complex concepts
    - Provide document summaries
    - Help you find specific information
    """)
    
    # Chat display
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your knowledge base..."):
        st.session_state.stats.update_stats('chat_messages')
        st.chat_message("user").write(prompt)
        
        # Add user message to history
        st.session_state.chat_history.append(HumanMessage(content=prompt))
        
        try:
            # Search knowledge base for relevant context
            search_results = st.session_state.search.semantic_search(prompt)
            
            # Format context from search results
            context = "\n\n".join([
                f"From {result.metadata.get('title', 'document')}:\n{result.content}"
                for result in search_results[:3]
            ])
            
            # Generate response using context
            llm = ChatOpenAI(temperature=0.7)
            system_prompt = """You are Project Oracle's AI Assistant, an intelligent and helpful guide that helps users understand and navigate their knowledge base.
            You have access to a custom knowledge base of documents and can help with:
            1. Answering questions about the content
            2. Providing guidance and onboarding support
            3. Explaining complex topics
            4. Finding specific information
            5. Summarizing documents
            
            Always be helpful, clear, and concise. If you're not sure about something, say so.
            Base your responses on the provided context when possible."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Context from knowledge base:\n{context}\n\nUser question: {prompt}")
            ]
            
            response = llm(messages)
            
            # Display assistant response
            st.chat_message("assistant").write(response.content)
            
            # Add assistant message to history
            st.session_state.chat_history.append(response)
            
            # Update stats
            st.session_state.stats.update_stats('queries_made')
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            logging.error(f"Chat error: {str(e)}", exc_info=True)

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
        docs_processed = st.session_state.stats.documents_processed
        total_docs = docs_processed if isinstance(docs_processed, int) else docs_processed.get('total', 0)
        st.metric("Documents Processed", total_docs)
    with col2:
        queries = st.session_state.stats.queries_made
        total_queries = queries if isinstance(queries, int) else queries.get('total', 0)
        st.metric("Queries Made", total_queries)
    with col3:
        messages = st.session_state.stats.chat_messages
        total_messages = messages if isinstance(messages, int) else messages.get('total', 0)
        st.metric("Messages Exchanged", total_messages)
    
    # Document Type Distribution
    st.subheader("Document Distribution")
    if st.session_state.stats.document_types:
        doc_types_df = pd.DataFrame(
            list(st.session_state.stats.document_types.items()),
            columns=['Type', 'Count']
        )
        fig = px.pie(doc_types_df, values='Count', names='Type')
        st.plotly_chart(fig)
    else:
        st.info("No documents processed yet.")
    
    # Popular Search Terms
    st.subheader("Popular Search Terms")
    if st.session_state.stats.search_terms:
        search_terms = pd.Series(st.session_state.stats.search_terms).value_counts()
        fig = px.bar(search_terms, title="Most Common Search Terms")
        st.plotly_chart(fig)
    else:
        st.info("No searches performed yet.")

class AdvancedSearch:
    def __init__(self, kb=None):
        self.kb = kb
        
    def semantic_search(self, query: str, num_results: int = 3) -> List[dict]:
        """Perform semantic search over the knowledge base."""
        try:
            results = self.kb.search(query, num_results)
            return results
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return []

def main():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'chat_input_key' not in st.session_state:
        st.session_state.chat_input_key = 0
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'stats' not in st.session_state:
        st.session_state.stats = SessionStats()
    if 'kb' not in st.session_state:
        st.session_state.kb = KnowledgeBase()
    if 'search' not in st.session_state:
        st.session_state.search = AdvancedSearch(kb=st.session_state.kb)
        
    # Configure page
    st.set_page_config(
        page_title="Project Oracle",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
        
    # Sidebar Navigation
    with st.sidebar:
        st.title("🔮 Project Oracle")
        st.markdown("## Navigation")
        
        pages = {
            "Home": "🏠",
            "Document Management": "📚",
            "Chat Interface": "🤖",
            "Advanced Search": "🔍",
            "Analytics Dashboard": "📊",
            "Knowledge Graph": "🕸️"
        }
        
        for page, emoji in pages.items():
            if st.button(f"{emoji} {page}"):
                st.session_state.current_page = page
        
        # Session Information
        st.markdown("---")
        st.markdown("### Session Info")
        session_duration = st.session_state.stats.get_session_duration()
        st.text(f"Duration: {str(session_duration).split('.')[0]}")
    
    # Main Content
    if st.session_state.current_page == "Home":
        homepage()
    elif st.session_state.current_page == "Document Management":
        document_management_interface(st.session_state.kb)
    elif st.session_state.current_page == "Chat Interface":
        chat_interface()
    elif st.session_state.current_page == "Advanced Search":
        advanced_search_interface(st.session_state.kb, st.session_state.search)
    elif st.session_state.current_page == "Analytics Dashboard":
        analytics_dashboard()
    elif st.session_state.current_page == "Knowledge Graph":
        knowledge_graph_interface(st.session_state.kb.knowledge_graph)

if __name__ == "__main__":
    main()
