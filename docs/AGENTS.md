# Agent System Documentation

## Overview

Project Oracle implements a multi-agent system using LangChain and LangGraph, featuring specialized agents for different tasks. Each agent is designed to handle specific types of queries and operations.

## Agent Types

### 1. Web Scraping Agent
```python
def create_webscrape_agent():
    """Specialized in web content extraction"""
    return create_react_agent(
        llm.bind(system_message="""
            Web scraping specialist responsibilities:
            1. URL extraction and validation
            2. Content scraping
            3. Markdown conversion
            4. File storage
            5. Content summarization
        """),
        scraping_tools
    )
```

#### Capabilities
- URL extraction from user queries
- Web content scraping via FireCrawl
- Markdown file generation
- Content summarization
- File system management

#### Tools
```python
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage",
        func=scraper.scrape_url
    )
]
```

### 2. Knowledge Base Agent
```python
def create_knowledge_agent():
    """Specialized in knowledge base queries"""
    return create_react_agent(
        llm.bind(system_message="""
            Knowledge base specialist responsibilities:
            1. Topic search and retrieval
            2. Article management
            3. Content organization
            4. Related content suggestions
        """),
        knowledge_tools
    )
```

#### Capabilities
- Topic search and retrieval
- Article management
- Fuzzy matching
- Related content linking
- Content summarization

#### Tools
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

### 3. Conversation Agent
```python
def conversation_node(state):
    """Handles general conversation"""
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}
```

#### Capabilities
- Natural language understanding
- Context maintenance
- General chat handling
- Response generation

## Agent Workflow

### 1. Router System
```python
def create_router():
    """Intelligent query routing"""
    return route_classifier(state) -> RouteResponse
```

#### Routing Logic
- Analyzes user input
- Determines appropriate agent
- Maintains conversation flow
- Handles agent transitions

### 2. State Management
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
```

### 3. Workflow Graph
```python
workflow = StateGraph(AgentState)
workflow.add_node("WebScrape", webscrape_node)
workflow.add_node("Knowledge", knowledge_node)
workflow.add_node("Conversation", conversation_node)
```

## Agent Communication

### Message Format
```python
{
    "messages": [
        SystemMessage(content="..."),
        HumanMessage(content="..."),
        AIMessage(content="...")
    ]
}
```

### Response Format
```python
{
    "messages": [
        HumanMessage(content="Response content")
    ]
}
```

## Agent Configuration

### System Messages
Each agent has specific instructions:
```python
# Web Scraping Agent
"""
You are a web scraping specialist. Your task is to:
1. Extract URLs from requests
2. Manage content extraction
3. Handle file storage
4. Provide summaries
"""

# Knowledge Base Agent
"""
You are a knowledge base specialist. Your task is to:
1. Handle information queries
2. Search and retrieve content
3. Suggest related topics
4. Present organized responses
"""
```

### Tool Configuration
```python
Tool(
    name="tool_name",
    description="Tool description",
    func=tool_function
)
```

## Error Handling

### Agent-Level Errors
```python
try:
    result = agent.invoke(state)
except Exception as e:
    return {
        "messages": [
            HumanMessage(content=f"Error: {str(e)}")
        ]
    }
```

### Workflow-Level Errors
```python
try:
    for step in workflow.stream(state):
        process_step(step)
except Exception as e:
    handle_workflow_error(e)
```

## Performance Considerations

### Agent Optimization
1. Response Caching
2. Tool Result Memoization
3. Context Management
4. Resource Cleanup

### Best Practices
1. Clear System Messages
2. Specific Tool Descriptions
3. Proper Error Handling
4. Efficient State Management

## Development Guidelines

### Adding New Agents
1. Create agent class/function
2. Define specialized tools
3. Configure system message
4. Add to workflow graph
5. Update router logic

### Modifying Existing Agents
1. Update system message
2. Modify tool set
3. Adjust error handling
4. Test thoroughly
5. Update documentation

### Testing Agents
1. Unit test tools
2. Test agent responses
3. Verify routing logic
4. Check error handling
5. Validate workflow integration 