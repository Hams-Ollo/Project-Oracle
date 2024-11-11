# Configuration Guide

## Environment Setup

### Required Environment Variables
```bash
# API Keys
FIRECRAWL_API_KEY=your-firecrawl-key    # Required for web scraping
OPENAI_API_KEY=your-openai-key          # Required for LLM functionality

# Optional Configuration
DEBUG_MODE=true                         # Enable detailed logging
```

### Directory Structure
```
project-oracle/
├── dev.py                 # Main application
├── knowledge_base.json    # Knowledge base data
├── scrape_dump/          # Scraped content storage
├── .env                  # Environment variables
└── docs/                 # Documentation
```

## System Configuration

### LLM Settings
```python
# Language Model Configuration
llm = ChatOpenAI(
    temperature=0.7,  # Higher for more creative responses
    model="gpt-3.5-turbo"  # Default model
)
```

### Workflow Configuration
```python
config = {
    "recursion_limit": 150,  # Maximum steps in workflow
    "timeout": 300          # Maximum execution time (seconds)
}
```

### Logging Configuration
```python
# Emoji-based logging indicators
EMOJIS = {
    'start': '🚀',  # Process initiation
    'chat': '💭',   # Chat messages
    'web': '🌐',    # Web operations
    'route': '🔄',  # Routing decisions
    'error': '❌',  # Error states
    'success': '✅', # Successful operations
    'info': 'ℹ️ ',   # Information messages
    'think': '🤔',  # Processing states
    'done': '🏁',   # Completion
    'warn': '⚠️ '    # Warning messages
}
```

## Agent Configuration

### Web Scraping Agent
```python
# FireCrawl Configuration
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage",
        func=scraper.scrape_url
    )
]
```

### Knowledge Base Agent
```python
# Knowledge Base Tools
knowledge_tools = [
    Tool(
        name="search_topic",
        description="Search knowledge base topics",
        func=kb.search_topic
    ),
    Tool(
        name="list_topics",
        description="List available topics",
        func=kb.list_topics
    ),
    Tool(
        name="get_article",
        description="Retrieve specific article",
        func=kb.get_article
    )
]
```

## File Storage

### Scrape Directory
```python
# Configuration for scraped content storage
scrape_dir = Path("scrape_dump")
```

### File Naming
```python
# Timestamp format for unique filenames
timestamp_format = "%Y%m%d_%H%M%S"
filename = f"{sanitized_url}_{timestamp}.md"
```

## Performance Settings

### Rate Limiting
- Web scraping: 10 requests per minute
- LLM calls: Based on API tier
- File operations: No specific limits

### Memory Management
```python
# Conversation history management
max_history_length = 50  # Maximum messages to retain
max_token_limit = 4000   # Maximum tokens per context
```

## Error Handling

### Retry Configuration
```python
# Retry settings for API calls
max_retries = 3
retry_delay = 2  # seconds
```

### Timeout Settings
```python
# Timeout configuration
scraping_timeout = 30    # seconds
api_timeout = 10         # seconds
workflow_timeout = 300   # seconds
```

## Development Settings

### Debug Mode
```python
# Enable detailed logging
DEBUG_MODE=true

# Debug log format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Testing Configuration
```python
# Test environment settings
TEST_MODE=true
MOCK_APIS=true
```

## Security Settings

### API Security
- API keys stored in environment variables
- No key exposure in logs
- Secure key rotation support

### File System Security
- Restricted file operations
- Sanitized filenames
- Protected storage directories

## Maintenance

### Cleanup Settings
```python
# Automatic cleanup configuration
max_file_age = 7        # days
max_storage_size = 1000  # MB
cleanup_interval = 24    # hours
```

### Backup Configuration
```python
# Backup settings
backup_interval = 24    # hours
max_backups = 7        # number of backups to keep
backup_directory = "backups/"
```

## Customization

### Adding New Tools
1. Define tool function
2. Create Tool instance
3. Add to appropriate agent
4. Update configuration

### Modifying Agents
1. Update system message
2. Modify tool set
3. Adjust configuration
4. Test changes

## Troubleshooting

### Common Issues
1. API key not found
2. Directory permissions
3. Rate limiting
4. Memory constraints

### Debug Steps
1. Enable DEBUG_MODE
2. Check log files
3. Verify configurations
4. Test connections 