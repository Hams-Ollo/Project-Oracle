# Testing Guide for Project Oracle

## Overview

Project Oracle uses a comprehensive testing strategy that includes:

- Unit tests for individual components
- Integration tests for system workflows
- Performance tests for search operations
- Memory usage monitoring

## Test Structure

```curl
tests/
├── test_vector_search.py    # Vector store unit tests
├── test_integration.py      # End-to-end workflow tests
├── test_performance.py      # Performance benchmarks
└── test_data/              # Test fixtures
    └── test_knowledge_base.json
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_vector_search.py
pytest tests/test_integration.py
pytest tests/test_performance.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src tests/
```

## Test Categories

### 1. Vector Search Tests

- Vector store initialization
- Document processing
- Search functionality
- Result formatting

### 2. Integration Tests

- End-to-end workflow testing
- Cross-component interaction
- Error handling
- Response formatting

### 3. Performance Tests

- Search response times
- Memory usage monitoring
- Concurrent operation handling
- Resource cleanup

## Performance Benchmarks

Expected performance metrics:

- Vector search: < 2.0 seconds
- Traditional search: < 1.0 seconds
- Memory increase: < 500MB
- Concurrent operations: < 2.0 seconds per query

## Test Data

The test suite uses a simplified knowledge base for testing:

- Star Wars topics
- Technical documentation
- Process information

## Writing New Tests

### Test Structure (Example)

```python
def test_new_feature():
    """Test description"""
    # Arrange
    # Set up test data and environment
    
    # Act
    # Execute the functionality
    
    # Assert
    # Verify the results
```

### Best Practices

1. Use descriptive test names
2. Include docstrings
3. Follow AAA pattern (Arrange-Act-Assert)
4. Clean up resources
5. Use appropriate fixtures

## Continuous Integration

Tests are run automatically on:

- Pull request creation
- Main branch updates
- Release tagging

## Troubleshooting

Common issues and solutions:

1. **Module Import Errors**
   - Ensure `pip install -e .` was run
   - Check Python path

2. **Test Data Issues**
   - Verify test_knowledge_base.json exists
   - Check file permissions

3. **Performance Test Failures**
   - Check system resources
   - Verify no competing processes

## Adding New Tests

1. Create test file in `tests/` directory
2. Add necessary fixtures
3. Implement test cases
4. Update documentation
5. Verify CI pipeline

## Coverage Requirements

- Minimum coverage: 80%
- Critical paths: 100%
- New features: 90%

## Future Improvements

Planned enhancements:

1. Property-based testing
2. Load testing
3. Chaos testing
4. API endpoint testing
