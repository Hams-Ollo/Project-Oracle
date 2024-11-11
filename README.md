# Project Oracle - Multi-Agent Chat System

## Overview

Project Oracle is an intelligent chat system featuring multiple specialized agents that can handle web scraping, knowledge base queries, and general conversation. Built with LangChain and OpenAI's GPT models, it provides a flexible and extensible framework for multi-agent interactions.

## 🌟 Features

### Core Capabilities

- **Multi-Agent System**: Specialized agents for different tasks
  - Web Scraping Agent: Extracts and saves web content
  - Knowledge Base Agent: Manages and queries stored information
  - Conversation Agent: Handles general chat interactions

### Technical Features

- **Intelligent Routing**: Automatically directs queries to appropriate agents
- **Flexible Knowledge Base**: JSON-based storage with fuzzy matching
- **Web Scraping**: Markdown conversion and storage of web content
- **Conversation Management**: Context-aware chat handling
- **Emoji-Enhanced Logging**: Visual feedback for system operations

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- FireCrawl API key
- Git (for version control)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/project-oracle.git
cd project-oracle
```

2. Create and activate virtual environment:

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - FIRECRAWL_API_KEY
```

### Usage

Run the application:
```bash
python dev.py
```

Example interactions:

- Web Scraping: "Can you scrape https://example.com?"
- Knowledge Query: "What do you know about the Jedi Order?"
- General Chat: "Hello, how are you today?"

## 📚 Documentation

Detailed documentation is available in the `docs` folder:

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [User Guide](docs/USER_GUIDE.md)

## 🛠️ Development

### Project Structure

```curl
project-oracle/
├── dev.py              # Main application file
├── knowledge_base.json # Knowledge base storage
├── scrape_dump/       # Scraped content storage
├── docs/              # Documentation
└── requirements.txt   # Dependencies
```

### Key Components

- **Agent System**: Specialized agents for different tasks
- **Router**: Intelligent query routing
- **Knowledge Base**: JSON-based information storage
- **Web Scraper**: FireCrawl-powered web content extraction

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed contribution guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

For security concerns, please see our [Security Guidelines](docs/SECURITY.md).

## 🐛 Troubleshooting

For common issues and solutions, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
