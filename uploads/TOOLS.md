# Tools Documentation

## Overview

Project Oracle uses LangChain's Tool framework to provide specialized functionality to its agents. Each tool is designed for a specific purpose and can be accessed by the appropriate agent.

## Current Tools

### Web Scraping Tools

```python
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage. Input should be a valid URL.",
        func=scraper.scrape_url
    )
]
```

#### Capabilities

- URL content extraction
- Markdown conversion
- File storage
- Content summarization

### Knowledge Base Tools

```python
knowledge_tools = [
    Tool(
        name="search_topic",
        description="Search for information about a specific topic",
        func=kb.search_topic
    ),
    Tool(
        name="list_topics",
        description="List all available topics",
        func=kb.list_topics
    ),
    Tool(
        name="get_article",
        description="Get a specific article by title",
        func=kb.get_article
    )
]
```

#### Capabilities (0.2.0)

- Topic search and retrieval
- Article management
- Content listing
- Related content discovery

## Tool Implementation

### Basic Tool Structure

```python
Tool(
    name: str,          # Unique identifier
    description: str,   # Clear usage instructions
    func: Callable,     # Implementation function
    return_direct: bool = False  # Whether to return result directly
)
```

### Function Requirements

```python
def tool_function(input_str: str) -> str:
    """
    Tool functions must:
    1. Accept a single string input
    2. Return a string output
    3. Handle their own errors
    4. Provide clear feedback
    """
    try:
        result = process(input_str)
        return format_result(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

## Creating New Tools

### Step 1: Define Function

```python
def new_tool_function(input_str: str) -> str:
    """
    Implementation of new functionality
    
    Args:
        input_str: User input or query
        
    Returns:
        str: Formatted response
    """
    # Implementation here
    return result
```

### Step 2: Create Tool

```python
new_tool = Tool(
    name="new_tool_name",
    description="Clear description of what the tool does and how to use it",
    func=new_tool_function
)
```

### Step 3: Add to Tool Set

```python
tool_set = [
    existing_tool,
    new_tool
]
```

## Best Practices

### Tool Design

1. **Single Responsibility**
   - Each tool should do one thing well
   - Clear input/output contract
   - Focused functionality

2. **Clear Description**
   - Explain what the tool does
   - Specify input requirements
   - Provide usage examples
   - Document limitations

3. **Error Handling**
   - Graceful error management
   - Informative error messages
   - Input validation
   - Safe failure modes

### Implementation Guidelines

1. **Input Processing**

   ```python
   def validate_input(input_str: str) -> bool:
       """Validate tool input"""
       if not input_str:
           raise ValueError("Empty input")
       # Additional validation
       return True
   ```

2. **Output Formatting**

   ```python
   def format_output(result: Any) -> str:
       """Format tool output"""
       return f"""Result:
       {result}
       
       Status: Success
       """
   ```

3. **Error Messages**

   ```python
   def handle_error(e: Exception) -> str:
       """Format error message"""
       return f"""Error occurred:
       Type: {type(e).__name__}
       Message: {str(e)}
       
       Please try again with valid input.
       """
   ```

## Testing Tools

### Unit Testing

```python
def test_tool():
    """Test tool functionality"""
    tool = Tool(name="test", func=test_function)
    result = tool.run("test input")
    assert isinstance(result, str)
    assert "expected output" in result
```

### Integration Testing

```python
async def test_tool_in_agent():
    """Test tool within agent"""
    agent = create_agent([tool])
    response = await agent.run("use test tool")
    assert response.success
```

## Maintenance

### Regular Updates

1. Review tool descriptions
2. Update functionality
3. Improve error handling
4. Enhance documentation

### Performance Monitoring

1. Track usage patterns
2. Monitor error rates
3. Measure response times
4. Optimize as needed

## Security Considerations

### Input Validation

- Sanitize user input
- Check URL safety
- Validate file operations
- Prevent injection attacks

### Resource Management

- Rate limiting
- Timeout handling
- Resource cleanup
- Access control

## Future Enhancements

### Planned Tools

1. Content Analysis Tool
2. Data Processing Tool
3. Format Conversion Tool
4. Enhanced Search Tool

### Improvements

1. Better error handling
2. Enhanced performance
3. More detailed logging
4. Extended capabilities
