# Project Oracle - Advanced Knowledge Management System

Project Oracle is a sophisticated knowledge management system built with modern AI technologies. It features advanced document processing, intelligent search capabilities, and automated knowledge organization. The system leverages cutting-edge NLP and machine learning techniques to provide powerful document analysis, topic modeling, and relationship discovery.

## 🌟 Key Features

- **Multi-Format Document Processing**: Support for various document types (PDF, DOCX, TXT, MD, Images)
- **Advanced Search Capabilities**:
  - Semantic search using embeddings
  - Faceted search with multiple dimensions
  - Topic-based document exploration
- **Intelligent Document Analysis**:
  - Automatic topic modeling (LDA/NMF)
  - Document clustering
  - Named entity recognition
  - Automatic tag generation
- **Knowledge Organization**:
  - Relationship tracking between documents
  - Automated metadata extraction
  - Dynamic topic categorization
- **Modern Web Interface**:
  - Streamlit-based dashboard
  - Interactive visualizations
  - Real-time search and filtering

## 🚀 Project Structure

```curl
project-oracle/
├── src/
│   ├── services/
│   │   ├── advanced_search.py    # Enhanced search functionality
│   │   ├── document_processor.py # Multi-format document processing
│   │   ├── knowledge_base.py     # Core knowledge management
│   │   ├── search_engine.py      # Search implementation
│   │   └── kb_config.py          # System configuration
│   └── utils/
│       └── text_utils.py         # Text processing utilities
├── frontend/
│   └── streamlit_app.py         # Web interface
├── tests/                       # Test suite
├── data/                       # Document storage
├── requirements.txt           # Project dependencies
└── README.md                # Project documentation
```

## 🛠️ Prerequisites

- Python 3.12+
- OpenAI API key (for advanced NLP features)
- Virtual environment

## ⚙️ Installation

Step 1. Clone the repository:

```bash
git clone https://github.com/yourusername/project-oracle.git
cd project-oracle
```

Step 2. Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

Step 3. Install dependencies:

```bash
pip install -r requirements.txt
```

Step 4. Set up environment variables:
Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Running the Application

Launch the web interface:

```bash
streamlit run frontend/streamlit_app.py
```

## 💡 Core Components

### Document Processing

- Multi-format support (PDF, DOCX, TXT, MD, Images)
- Automatic text extraction and chunking
- Metadata extraction
- Document summarization

### Advanced Search

- Semantic search using embeddings
- Faceted search with filters for:
  - Document types
  - Topics
  - Authors
  - Date ranges
  - Tags
- Topic-based exploration

### Knowledge Organization

- Automatic topic modeling
- Document clustering
- Relationship tracking
- Tag generation using:
  - KeyBERT extraction
  - Named Entity Recognition
  - LLM-based topic identification

### Web Interface

- Document upload and management
- Interactive search
- Topic visualization
- Faceted navigation
- Document previews

## 🔧 Configuration

Key configuration options in `kb_config.py`:

- Document processing parameters
- Search settings
- Model configurations
- Storage paths

## 📊 Performance Considerations

- Efficient document chunking
- Optimized search indexing
- Caching for frequently accessed content
- Batched processing for large documents

## 🐛 Troubleshooting

Common issues and solutions:

1. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated
2. **API Key Issues**: Verify OpenAI API key in `.env` file
3. **Memory Issues**: Adjust chunk sizes for large documents
4. **Search Performance**: Check index status and rebuild if necessary

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
