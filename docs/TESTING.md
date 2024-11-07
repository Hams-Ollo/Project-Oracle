# Testing Documentation

## Overview

Project Oracle implements a comprehensive testing strategy across multiple levels to ensure system reliability and functionality.

## Test Structure

### Unit Tests

#### Agent Tests

```python
# tests/unit/test_agents.py
def test_agent_initialization():
    """Test agent initialization and configuration"""
    agent = Agent(
        name="test_agent",
        model="gpt-4o-mini",
        instructions="Test instructions"
    )
    assert agent.name == "test_agent"
    assert agent.model == "gpt-4o-mini"

def test_agent_with_docs():
    """Test AgentWithDocs wrapper functionality"""
    kb = KnowledgeBase()
    agent = AgentWithDocs(
        agent=Agent(name="test", model="gpt-4o-mini"),
        knowledge_base=kb
    )
    context = agent.get_context_from_docs("test query")
    assert isinstance(context, str)
```

#### Knowledge Base Tests

```python
# tests/unit/test_knowledge_base.py
def test_knowledge_base_search():
    """Test knowledge base search functionality"""
    kb = KnowledgeBase()
    results = kb.search("project setup")
    assert len(results) > 0
    assert all(isinstance(r, dict) for r in results)
```

### Integration Tests

#### Agent Interaction Tests

```python
# tests/integration/test_agent_interactions.py
async def test_agent_handoff():
    """Test agent handoff functionality"""
    swarm = Swarm()
    current_agent = onboarding_agent
    response = await swarm.run(
        agent=current_agent,
        messages=[{"role": "user", "content": "technical question"}]
    )
    assert "next_agent" in response
```

#### System Flow Tests

```python
# tests/integration/test_system_flow.py
async def test_complete_conversation_flow():
    """Test end-to-end conversation flow"""
    messages = []
    response = await process_conversation(
        "How do I set up the project?",
        messages
    )
    assert "setup" in response.lower()
    assert len(messages) > 1
```

### End-to-End Tests

#### User Interaction Tests

```python
# tests/e2e/test_user_interactions.py
def test_complete_user_session():
    """Test complete user interaction session"""
    session = UserSession()
    responses = session.process_interactions([
        "Hello",
        "How do I start?",
        "Tell me about the architecture"
    ])
    assert len(responses) == 3
    assert all(isinstance(r, str) for r in responses)
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_agents.py
```

### Coverage Testing

```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate coverage report
pytest --cov=src --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

## Writing Tests

### Test Case Guidelines

1. Test Structure

```python
def test_function_name():
    """Clear description of what is being tested"""
    # Setup
    agent = create_test_agent()
    
    # Execute
    result = agent.process("test")
    
    # Assert
    assert isinstance(result, dict)
    assert "response" in result
```

2. Mocking External Services

```python
@patch('openai.ChatCompletion.create')
def test_llm_interaction(mock_completion):
    """Test LLM interaction with mocked response"""
    mock_completion.return_value = {
        'choices': [{'message': {'content': 'test response'}}]
    }
    response = agent.get_completion([])
    assert response == "test response"
```

### Test Categories

1. Functional Tests

- Agent behavior
- Knowledge base operations
- Message processing
- Context management

2. Error Handling Tests

```python
def test_invalid_input_handling():
    """Test handling of invalid input"""
    with pytest.raises(ValueError):
        agent.process("")
```

3. Performance Tests

```python
def test_response_time():
    """Test response time is within acceptable range"""
    start_time = time.time()
    agent.process("test query")
    duration = time.time() - start_time
    assert duration < 2.0  # Maximum 2 seconds
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
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
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

## Test Data Management

### Fixtures

```python
# tests/conftest.py
@pytest.fixture
def test_knowledge_base():
    """Provide test knowledge base"""
    return KnowledgeBase("tests/data/test_knowledge_base.json")

@pytest.fixture
def test_agent(test_knowledge_base):
    """Provide test agent with knowledge base"""
    return AgentWithDocs(
        agent=Agent(name="test", model="gpt-4o-mini"),
        knowledge_base=test_knowledge_base
    )
```

### Test Data

```json
// tests/data/test_knowledge_base.json
{
    "test_data": {
        "query": "test",
        "expected_response": "test response"
    }
}
```

## Performance Testing

### Load Testing

```python
def test_concurrent_requests():
    """Test handling of concurrent requests"""
    async def make_request():
        return await agent.process("test")
    
    results = asyncio.run(asyncio.gather(
        *[make_request() for _ in range(10)]
    ))
    assert len(results) == 10
```

### Memory Usage

```python
def test_memory_usage():
    """Test memory usage remains within limits"""
    import memory_profiler
    
    @memory_profiler.profile
    def process_large_query():
        agent.process("large test query")
    
    process_large_query()
```
