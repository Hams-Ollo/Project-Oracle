# Knowledge Base Development Guide

## Overview

This guide provides detailed instructions for developers to add and manage information in Project Oracle's knowledge base system. The knowledge base uses ChromaDB for vector storage and semantic search capabilities, allowing efficient retrieval of information through both traditional and vector-based search methods.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Setup Requirements](#setup-requirements)
3. [Adding Knowledge Base Entries](#adding-knowledge-base-entries)
4. [Vector Store Operations](#vector-store-operations)
5. [Testing Your Changes](#testing-your-changes)
6. [Best Practices](#best-practices)

## System Architecture

Project Oracle's knowledge base consists of two main components:

1. **VectorStore Service**:
   - Handles document embeddings using OpenAI
   - Manages similarity search via ChromaDB
   - Handles document chunking and processing
   - Maintains metadata relationships

2. **KnowledgeBase Service**:
   - Manages JSON data structure
   - Coordinates search operations
   - Handles data validation
   - Provides tool interfaces

## Setup Requirements

Before working with the knowledge base, ensure you have:

1. **Environment Setup**:
   - Python 3.11 or higher
   - Virtual environment activated
   - Dependencies installed via `pip install -r requirements.txt`

2. **API Keys**:
   - OpenAI API key in `.env`
   - Other required credentials

3. **Directory Structure**:

   ```curl
   project-oracle/
   ├── knowledge_base.json
   ├── vector_store/
   │   ├── chroma.sqlite3
   │   └── index/
   └── scrape_dump/
   ```

## Adding Knowledge Base Entries

### 1. JSON Structure

The knowledge base data follows this structure:

```json
{
    "topics": {
        "category_name": {
            "topic_name": {
                "definition": "Clear definition",
                "history": "Historical context",
                "key_concepts": ["concept1", "concept2"],
                "important_figures": ["figure1", "figure2"],
                "cultural_significance": "Impact description"
            }
        }
    },
    "articles": {
        "category_name": {
            "article_name": {
                "title": "Article Title",
                "summary": "Brief overview",
                "key_points": ["point1", "point2"],
                "content": "Detailed content"
            }
        }
    }
}
```

### 2. Adding New Topics

1. **Choose Category**:
   - Use existing category or create new
   - Follow naming conventions
   - Maintain hierarchy

2. **Create Topic Content**:

   ```python
   new_topic = {
       "definition": "Clear, concise definition",
       "history": "Historical background",
       "key_concepts": ["concept1", "concept2"],
       "important_figures": ["person1", "person2"],
       "cultural_significance": "Impact description"
   }
   ```

3. **Update Knowledge Base**:

   ```python
   kb.data["topics"]["category_name"]["new_topic"] = new_topic
   kb._initialize_vector_store()  # Rebuild vector store
   ```

## Vector Store Operations

### 1. Document Processing

```python
def process_documents(content: dict) -> List[Document]:
    """Convert content to vector store format"""
    documents = []
    for category, topics in content.items():
        for topic, details in topics.items():
            doc = create_document(category, topic, details)
            documents.append(doc)
    return documents
```

### 2. Search Performance Settings

1. **Vector Search**:

   ```python
   results = kb.search("query", search_type="vector")
   ```

2. **Traditional Search**:

   ```python
   results = kb.search("query", search_type="traditional")
   ```

3. **Hybrid Search**:

   ```python
   results = kb.search("query", search_type="hybrid")
   ```

## Testing Your Changes

### 1. Unit Tests

```python
def test_knowledge_base():
    kb = KnowledgeBase()
    
    # Test topic addition
    result = kb.add_topic("category", "topic", topic_data)
    assert result.success
    
    # Test search functionality
    search_result = kb.search("test query")
    assert search_result is not None
```

### 2. Integration Tests

```python
def test_vector_store_integration():
    kb = KnowledgeBase()
    vs = VectorStore()
    
    # Test document processing
    docs = vs.process_json_data(test_data)
    assert len(docs) > 0
    
    # Test search integration
    results = kb.search("test", search_type="hybrid")
    assert results is not None
```

## Best Practices

### 1. Content Management

- Use clear, concise definitions
- Include relevant metadata
- Maintain consistent formatting
- Update related content
- Preserve context in chunks

### 2. Vector Store Management

- Rebuild after significant changes
- Monitor embedding quality
- Optimize chunk sizes
- Maintain metadata relationships
- Regular performance testing

### 3. Search Optimization

- Use appropriate search types
- Balance chunk sizes
- Monitor search performance
- Optimize metadata usage
- Regular accuracy testing

### 4. Error Handling

```python
try:
    kb.add_topic(category, topic, data)
except ValueError as e:
    log_step('error', f"Invalid data format: {e}")
except Exception as e:
    log_step('error', f"Unexpected error: {e}")
```

## Performance Considerations

### 1. Vector Store

- Optimal chunk size: 1000 tokens
- Chunk overlap: 200 tokens
- Regular reindexing
- Cache management
- Batch processing

### 2. Search Operations

- Default k=3 for vector search
- Hybrid search timeout: 30s
- Result caching
- Query optimization
- Performance monitoring

## Maintenance

### 1. Regular Tasks

- Validate JSON structure
- Update embeddings
- Clean unused vectors
- Optimize indexes
- Update documentation

### 2. Monitoring

- Search response times
- Embedding quality
- Storage usage
- Error rates
- User feedback

## Troubleshooting

### Common Issues

1. **Vector Store Errors**:
   - Clear vector store directory
   - Rebuild embeddings
   - Check API keys
   - Verify data format

2. **Search Problems**:
   - Check query format
   - Verify data exists
   - Test different search types
   - Monitor performance

3. **Data Integration**:
   - Validate JSON
   - Check relationships
   - Verify metadata
   - Test consistency

## Future Improvements

1. **Planned Enhancements**:
   - Advanced metadata
   - Improved chunking
   - Better context preservation
   - Enhanced search algorithms

2. **Optimization Goals**:
   - Faster search
   - Better accuracy
   - Reduced storage
   - Improved scalability
