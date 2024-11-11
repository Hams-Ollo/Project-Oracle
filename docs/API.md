# API Documentation

## System Components

### Core Classes

#### 1. WebScraper

```python
class WebScraper:
    """Web scraping tool using FireCrawl"""
    
    def __init__(self, api_key: str):
        """Initialize with FireCrawl API key"""
        
    def scrape_url(self, url: str) -> str:
        """Scrape and save webpage content"""
        
    def save_markdown(self, content: str, url: str) -> str:
        """Save content as markdown file"""
```

#### 2. KnowledgeBase

```python
class KnowledgeBase:
    """Knowledge base management system"""
    
    def __init__(self, json_path: str = "knowledge_base.json"):
        """Initialize from JSON file"""
        
    def search_topic(self, topic: str) -> str:
        """Search for topic information"""
        
    def list_topics(self) -> str:
        """List all available topics"""
        
    def get_article(self, title: str) -> str:
        """Retrieve specific article"""
```

### Agent System

#### 1. Agent Creation

```python
def create_webscrape_agent() -> Agent:
    """Create web scraping specialist agent"""
    return create_react_agent(
        llm.bind(system_message=...), 
        scraping_tools
    )

def create_knowledge_agent() -> Agent:
    """Create knowledge base specialist agent"""
    return create_react_agent(
        llm.bind(system_message=...), 
        knowledge_tools
    )
```

#### 2. Node Handlers

```python
def webscrape_node(state: dict) -> dict:
    """Handle web scraping operations"""
    return {"messages": [HumanMessage(content=...)]}

def knowledge_node(state: dict) -> dict:
    """Handle knowledge base queries"""
    return {"messages": [HumanMessage(content=...)]}

def conversation_node(state: dict) -> dict:
    """Handle general conversation"""
    return {"messages": [response]}
```

### Workflow Management

#### 1. State Definition

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
```

#### 2. Routing

```python
class RouteResponse(BaseModel):
    """Model for routing decisions"""
    next: Literal["FINISH", "WebScrape", "Knowledge", "Conversation"]
```

## Tools

### Web Scraping Tools

```python
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage",
        func=scraper.scrape_url
    )
]
```

### Knowledge Base Tools

```python
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

## Response Formats

### Web Scraping Response

```python
{
    "success": True,
    "filepath": "scrape_dump/example_com_20240318_123456.md",
    "summary": "Content summary...",
    "content": "Full content..."
}
```

### Knowledge Base Response

```python
{
    "topic": "Topic name",
    "definition": "Topic definition",
    "key_concepts": ["concept1", "concept2"],
    "important_figures": ["figure1", "figure2"],
    "cultural_significance": "Significance details",
    "related_topics": ["topic1", "topic2"]
}
```

## Error Handling

### Standard Error Response

```python
{
    "error": True,
    "message": "Error description",
    "type": "ErrorType",
    "suggestions": ["suggestion1", "suggestion2"]
}
```

### Error Types

1. WebScrapingError
   - URL_INVALID
   - SCRAPING_FAILED
   - SAVE_FAILED

2. KnowledgeBaseError
   - TOPIC_NOT_FOUND
   - ARTICLE_NOT_FOUND
   - LOAD_FAILED

3. SystemError
   - ROUTING_FAILED
   - AGENT_CREATION_FAILED
   - WORKFLOW_ERROR

## Usage Examples

### Web Scraping

```python
# Initialize scraper
scraper = WebScraper(FIRECRAWL_API_KEY)

# Scrape webpage
result = scraper.scrape_url("https://example.com")
```

### Knowledge Base

```python
# Initialize knowledge base
kb = KnowledgeBase()

# Search topic
result = kb.search_topic("Jedi Order")

# List topics
topics = kb.list_topics()
```

### Workflow

```python
# Create workflow
workflow = create_chat_workflow()

# Process message
result = workflow.process({
    "messages": [HumanMessage(content="query")]
})
```

## Configuration

### Environment Variables

```python
FIRECRAWL_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
```

### System Configuration

```python
config = {
    "recursion_limit": 150,
    "timeout": 300
}
```

## Logging

### Log Format

```python
log_step(emoji: str, message: str):
    """Log with emoji indicator"""
    print(f"\n{EMOJIS[emoji]} {message}")
```

### Log Levels

- 'start': Process initiation
- 'chat': Chat messages
- 'web': Web operations
- 'route': Routing decisions
- 'error': Error states
- 'success': Successful operations
- 'info': Information messages
- 'think': Processing states
- 'done': Completion
- 'warn': Warning messages
