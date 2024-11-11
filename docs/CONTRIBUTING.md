# Contributing to Project Oracle

## Overview

Project Oracle welcomes contributions! This document provides guidelines for contributing to the project, setting up your development environment, and submitting changes.

## Development Environment Setup

### Prerequisites

- Python 3.12+
- Git
- OpenAI API key
- FireCrawl API key

### Initial Setup

1. Fork and Clone

```bash
git clone https://github.com/yourusername/project-oracle.git
cd project-oracle
```

Step B: Virtual Environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

Step C: Dependencies

```bash
pip install -r requirements.txt
```

Step D: Environment Configuration

```bash
cp .env.example .env
# Edit .env with required API keys:
OPENAI_API_KEY=your-key-here
FIRECRAWL_API_KEY=your-key-here
```

## Code Style Guidelines

### Python Standards

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Include docstrings for all classes and functions

### Example Function Format

```python
def process_message(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Process user message with optional context.
    
    Args:
        message: User input message
        context: Optional context dictionary
        
    Returns:
        Dict containing response and metadata
        
    Raises:
        ValueError: If message is empty
    """
    if not message.strip():
        raise ValueError("Message cannot be empty")
    
    return {"response": process(message, context)}
```

## Component Development

### Adding New Agents

Step A: Create agent class/function:

```python
def create_new_agent():
    """Create specialized agent"""
    return create_react_agent(
        llm.bind(system_message="..."),
        agent_tools
    )
```

Step B: Define tools:

```python
agent_tools = [
    Tool(
        name="tool_name",
        description="Tool description",
        func=tool_function
    )
]
```

Step C: Add to workflow:

```python
workflow.add_node("NewAgent", new_agent_node)
```

### Modifying Knowledge Base

Step A: Follow JSON schema:

```json
{
    "topics": {
        "topic_key": {
            "definition": "Topic definition",
            "key_concepts": ["concept1", "concept2"],
            "important_figures": ["figure1", "figure2"]
        }
    }
}
```

Step B: Update topic mappings

Step C: Test search functionality

Step D: Document changes

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_agents.py
pytest tests/test_knowledge_base.py

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests

```python
def test_agent_response():
    """Test agent response generation"""
    agent = create_webscrape_agent()
    result = agent.invoke({
        "messages": [
            HumanMessage(content="test message")
        ]
    })
    assert isinstance(result, dict)
```

## Documentation

### Code Documentation

- Clear docstrings
- Type hints
- Inline comments for complex logic
- Usage examples

### Markdown Files

- Clear structure
- Code examples
- Updated TOC
- Linked references

## Git Workflow

### Branch Naming

```bash
feature/add-new-agent
bugfix/fix-routing-error
docs/update-readme
test/add-agent-tests
```

### Commit Messages

```bash
feat(agents): add new research agent
fix(kb): resolve knowledge base search
docs(api): update API documentation
test(core): add unit tests for base agent
```

## Pull Request Process

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Documentation
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Code review by maintainers
2. CI/CD checks pass
3. Documentation updated
4. Tests added/updated
5. CHANGELOG.md updated

## Development Tools

### Code Quality

```bash
# Formatting
black .
isort .

# Linting
flake8 .

# Type checking
mypy .
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
```

## Release Process

### Version Updates

1. Update version in setup.py
2. Update CHANGELOG.md
3. Create release branch
4. Tag release
5. Update documentation

### Release Commands

```bash
# Create release branch
git checkout -b release/v0.2.0

# Tag release
git tag -a v0.2.0 -m "Release version 0.2.0"

# Push to remote
git push origin v0.2.0
```

## Support

### Getting Help

- Review documentation
- Check existing issues
- Join discussions
- Contact maintainers

### Reporting Issues

- Use issue templates
- Provide reproduction steps
- Include relevant logs
- Tag appropriately
