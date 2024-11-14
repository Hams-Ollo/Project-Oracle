# Project Oracle - AI Assistant with Web Scraping & Knowledge Base

A modular AI assistant that combines web scraping capabilities with a internal custom knowledge base (insert_use_case_here), powered by LangChain, LangGraph, and OpenAI.

## 🌟 Features

- **Intelligent Conversation Routing**: Automatically directs queries to specialized agents
- **Web Content Scraping**: Extract and store content from websites
- **Knowledge Base Integration**: Query and retrieve KNowledge Base information
- **Modular Architecture**: Clean separation of concerns for maintainability
- **Extensible Design**: Easy to add new agents and capabilities

## 🚀 Project Structure

```curl
project-oracle/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py        # Environment and app settings
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── agents.py         # AI agent definitions
│   │   └── workflow.py       # Conversation workflow
│   ├── services/             # External services
│   │   ├── __init__.py
│   │   ├── web_scraper.py   # Web scraping functionality
│   │   └── knowledge_base.py # Knowledge base operations
│   └── interface/           # User interaction
│       ├── __init__.py
│       └── chat.py         # Chat interface
├── knowledge_base.json     # Knowledge base storage
├── scrape_dump/           # Scraped content storage
├── requirements.txt       # Project dependencies
├── setup.py              # Package configuration
└── README.md            # Project documentation
```

## 🛠️ Prerequisites

- Python 3.11+
- OpenAI API key
- FireCrawl API key

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

Step 3. Install the package in development mode:

```bash
pip install -e .
```

Step 4. Set up environment variables:
Create a `.env` file in the project root:

```env
FIRECRAWL_API_KEY=your_firecrawl_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Running the Application

Run the application using:

```bash
python src/main.py
```

## 💬 Usage

The assistant supports three main types of interactions:

Step 1. **General Conversation**

```bash
You: Hello! How are you?
```

Step 2. **Web Scraping**

```bash
You: Can you scrape https://example.com for me?
```

Step 3. **Knowledge Base Queries**

```bash
You: What do you know about the Jedi Order?
You: List all available topics
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔍 Core Components

- **Web Scraper**: FireCrawl-powered content extraction
- **Knowledge Base**: JSON-based information storage
- **Agent System**: Specialized agents for different tasks
- **Router**: Intelligent query routing
- **Chat Interface**: Command-line interaction

## ⚠️ Error Handling

The application includes comprehensive error handling for:

- Invalid API keys
- Failed web scraping attempts
- Knowledge base query errors
- User input validation

## 🔄 Workflow

1. User input is received through the chat interface
2. The router analyzes the input and directs it to the appropriate agent
3. The agent processes the request using available tools
4. Results are formatted and presented to the user

## 📊 Performance

- Configurable recursion limits
- Timeout handling
- Efficient conversation history management
- Optimized knowledge base queries

## 🐛 Troubleshooting

If you encounter the "No module named 'src'" error, ensure you:

1. Have installed the package with `pip install -e .`
2. Are running from the project root directory
3. Have activated your virtual environment

## 📚 Documentation

For more detailed information, see the documentation in the `docs/` directory.
