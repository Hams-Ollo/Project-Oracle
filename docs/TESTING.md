# Testing Documentation

## Overview

Project Oracle requires comprehensive testing across multiple components: agent functionality, routing logic, knowledge base operations, and web scraping capabilities.

## Test Structure

### 1. Unit Tests

#### Agent Tests
```python
def test_webscrape_agent():
    """Test web scraping agent functionality"""
    agent = create_webscrape_agent()
    result = agent.invoke({
        "messages": [
            HumanMessage(content="Scrape https://example.com")
        ]
    })
    assert isinstance(result, dict)
    assert "output" in result or "messages" in result

def test_knowledge_agent():
    """Test knowledge base agent functionality"""
    agent = create_knowledge_agent()
    result = agent.invoke({
        "messages": [
            HumanMessage(content="What do you know about the Jedi Order?")
        ]
    })
    assert isinstance(result, dict)
    assert "output" in result or "messages" in result
```

#### Knowledge Base Tests
```python
def test_knowledge_base():
    """Test knowledge base operations"""
    kb = KnowledgeBase()
    
    # Test topic search
    result = kb.search_topic("Jedi Order")
    assert "Definition" in result
    assert "Key Concepts" in result
    
    # Test article retrieval
    result = kb.get_article("The Jedi Code")
    assert "Content" in result
    assert "Summary" in result
```

#### Web Scraping Tests
```python
def test_web_scraper():
    """Test web scraping functionality"""
    scraper = WebScraper(FIRECRAWL_API_KEY)
    
    # Test URL scraping
    result = scraper.scrape_url("https://example.com")
    assert "Successfully scraped" in result
    
    # Test file saving
    assert Path("scrape_dump").exists()
```

### 2. Integration Tests

#### Workflow Tests
```python
def test_workflow_routing():
    """Test workflow routing logic"""
    workflow = create_chat_workflow()
    
    # Test web scraping route
    result = workflow.invoke({
        "messages": [
            HumanMessage(content="Scrape https://example.com")
        ]
    })
    assert "WebScrape" in str(result)
    
    # Test knowledge base route
    result = workflow.invoke({
        "messages": [
            HumanMessage(content="Tell me about the Jedi")
        ]
    })
    assert "Knowledge" in str(result)
```

#### Agent Interaction Tests
```python
def test_agent_interactions():
    """Test agent interactions and handoffs"""
    workflow = create_chat_workflow()
    
    # Test conversation flow
    results = []
    for step in workflow.stream({
        "messages": [
            HumanMessage(content="Hello, tell me about the Jedi")
        ]
    }):
        results.append(step)
    
    assert len(results) > 0
    assert any("Knowledge" in str(step) for step in results)
```

### 3. System Tests

#### End-to-End Tests
```python
def test_complete_conversation():
    """Test complete conversation flow"""
    workflow = create_chat_workflow()
    
    test_inputs = [
        "Hello there",
        "What do you know about the Jedi?",
        "Can you scrape https://example.com?",
        "Goodbye"
    ]
    
    for input_text in test_inputs:
        result = next(workflow.stream({
            "messages": [HumanMessage(content=input_text)]
        }))
        assert result is not None
```

## Test Configuration

### Environment Setup
```python
# test_config.py
import pytest
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment"""
    load_dotenv()
    # Set up mock API responses
    # Initialize test knowledge base
```

### Mock Data
```python
# test_data.py
TEST_KNOWLEDGE_BASE = {
    "topics": {
        "test_topic": {
            "definition": "Test definition",
            "key_concepts": ["concept1", "concept2"]
        }
    },
    "articles": {
        "test_article": {
            "title": "Test Article",
            "content": "Test content"
        }
    }
}
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/system/

# Run with coverage
pytest --cov=src tests/
```

### Test Parameters
```python
@pytest.mark.parametrize("input_text,expected_route", [
    ("Hello", "Conversation"),
    ("Tell me about Jedi", "Knowledge"),
    ("Scrape https://example.com", "WebScrape")
])
def test_router(input_text, expected_route):
    """Test router with various inputs"""
    router = create_router()
    result = router({"messages": [HumanMessage(content=input_text)]})
    assert result["next"] == expected_route
```

## Error Testing

### Agent Error Handling
```python
def test_agent_errors():
    """Test agent error handling"""
    agent = create_webscrape_agent()
    
    # Test invalid URL
    result = agent.invoke({
        "messages": [
            HumanMessage(content="Scrape invalid-url")
        ]
    })
    assert "error" in str(result).lower()
```

### System Error Recovery
```python
def test_system_recovery():
    """Test system error recovery"""
    workflow = create_chat_workflow()
    
    # Test API failure recovery
    with mock.patch('openai.ChatCompletion.create', side_effect=Exception):
        result = next(workflow.stream({
            "messages": [HumanMessage(content="Hello")]
        }))
        assert "error" in str(result).lower()
```

## Performance Testing

### Response Time Tests
```python
def test_response_times():
    """Test response time requirements"""
    workflow = create_chat_workflow()
    
    start_time = time.time()
    next(workflow.stream({
        "messages": [HumanMessage(content="Hello")]
    }))
    duration = time.time() - start_time
    
    assert duration < 2.0  # Maximum 2 seconds
```

### Load Testing
```python
def test_concurrent_requests():
    """Test handling of concurrent requests"""
    workflow = create_chat_workflow()
    
    async def make_request():
        return await workflow.astream({
            "messages": [HumanMessage(content="Hello")]
        })
    
    results = asyncio.run(asyncio.gather(
        *[make_request() for _ in range(10)]
    ))
    assert len(results) == 10
```

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```