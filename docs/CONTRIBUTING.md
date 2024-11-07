# Contributing to Project Oracle

## Getting Started

### Development Environment Setup

1. Fork and Clone

```bash
git clone https://github.com/your-username/project-oracle.git
cd project-oracle
```

2. Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Unix/MacOS
.\venv\Scripts\activate   # Windows
```

3. Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Development Process

### Code Style Guidelines

1. Python Standards
   - Follow PEP 8 style guide
   - Use type hints for all functions
   - Maximum line length: 88 characters
   - Use docstrings for all classes and functions

2. Example Function Format

```python
def process_message(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Process user message with optional context.
    
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
    
    # Function implementation
    return {"response": "processed message"}
```

### Documentation Standards

1. Code Documentation
   - Clear, concise docstrings
   - Type hints for all functions
   - Inline comments for complex logic
   - Example usage where appropriate

2. Markdown Files
   - Clear headings and structure
   - Code examples with syntax highlighting
   - Updated table of contents
   - Links to related documentation

### Git Workflow

1. Branch Naming

```bash
feature/add-new-agent      # New features
bugfix/fix-context-error   # Bug fixes
docs/update-api-docs       # Documentation updates
test/add-agent-tests       # Test additions
```

2. Commit Messages

```bash
# Format
<type>(<scope>): <description>

# Examples
feat(agents): add new research agent capability
fix(kb): resolve knowledge base search issue
docs(api): update API documentation
test(core): add unit tests for base agent
```

## Pull Request Process

### 1. Preparation Checklist

- [ ] Update documentation
- [ ] Add/update tests
- [ ] Run linting checks
- [ ] Update CHANGELOG.md
- [ ] Resolve merge conflicts

### 2. PR Template

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

### 3. Code Review Guidelines

- Address all reviewer comments
- Maintain test coverage (minimum 80%)
- Follow up with requested changes
- Keep PR scope focused

## Testing Guidelines

### 1. Unit Tests

```python
def test_agent_response():
    """Test agent response generation"""
    agent = Agent(name="test", model="gpt-4o-mini")
    response = agent.process("test message")
    assert isinstance(response, dict)
    assert "content" in response
```

### 2. Integration Tests

```python
async def test_agent_knowledge_base():
    """Test agent interaction with knowledge base"""
    kb = KnowledgeBase()
    agent = AgentWithDocs(Agent(...), kb)
    context = await agent.get_context_from_docs("test query")
    assert context is not None
```

## Development Tools

### 1. Code Quality

```bash
# Run linting
flake8 .
black .
isort .

# Run type checking
mypy .
```

### 2. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. tests/
```

### 3. Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## Release Process

### 1. Version Bump

- Update version in setup.py
- Update CHANGELOG.md
- Create release branch

### 2. Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared

### 3. Release Commands

```bash
# Create release branch
git checkout -b release/v1.0.0

# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push to remote
git push origin v1.0.0
```
