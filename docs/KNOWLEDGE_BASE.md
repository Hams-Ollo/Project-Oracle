# Knowledge Base Documentation

## Overview

Project Oracle uses a JSON-based knowledge base system with flexible topic matching and article management. The system supports fuzzy matching, related content linking, and comprehensive topic/article relationships.

## Structure

### JSON Schema
```json
{
    "topics": {
        "topic_key": {
            "definition": "Topic definition",
            "key_concepts": ["concept1", "concept2"],
            "important_figures": ["figure1", "figure2"],
            "cultural_significance": "Significance details"
        }
    },
    "articles": {
        "article_key": {
            "title": "Article Title",
            "summary": "Brief summary",
            "key_points": ["point1", "point2"],
            "content": "Full article content"
        }
    }
}
```

### Topic Structure
```python
topic = {
    "definition": str,          # Main topic definition
    "key_concepts": List[str],  # Related concepts
    "important_figures": List[str],  # Key figures
    "cultural_significance": str  # Cultural context
}
```

### Article Structure
```python
article = {
    "title": str,              # Article title
    "summary": str,            # Brief summary
    "key_points": List[str],   # Main points
    "content": str             # Full content
}
```

## Implementation

### KnowledgeBase Class
```python
class KnowledgeBase:
    def __init__(self, json_path: str = "knowledge_base.json"):
        """Initialize knowledge base from JSON file"""
        
    def search_topic(self, topic: str) -> str:
        """Search for topic information"""
        
    def list_topics(self) -> str:
        """List all available topics"""
        
    def get_article(self, title: str) -> str:
        """Retrieve specific article"""
```

### Flexible Matching System

#### Topic Aliases
```python
self.topic_aliases = {
    "original_key": "topic_key",
    "alternative_name": "topic_key",
    "key_concept": "topic_key"
}
```

#### Article Aliases
```python
self.article_aliases = {
    "article_title": "article_key",
    "alternative_title": "article_key",
    "key_point_term": "article_key"
}
```

## Usage

### Searching Topics
```python
# Direct search
result = kb.search_topic("Jedi Order")

# Fuzzy matching
result = kb.search_topic("Jedi")  # Will match "Jedi Order"
```

### Retrieving Articles
```python
# Direct retrieval
article = kb.get_article("The Jedi Code")

# Partial matching
article = kb.get_article("Jedi Code")  # Will find "The Jedi Code"
```

### Listing Content
```python
# List all topics
topics = kb.list_topics()

# List all articles
articles = kb.list_articles()
```

## Tools Integration

### Knowledge Tools
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

### Topic Response
```python
"""
Topic: [topic_name]

Definition: [definition]

Key Concepts: [concept1, concept2, ...]

Important Figures: [figure1, figure2, ...]

Cultural Significance: [significance]

Related Topics: [topic1, topic2, ...]

Related Articles: [article1, article2, ...]
"""
```

### Article Response
```python
"""
Article: [title]

Summary: [summary]

Key Points:
- [point1]
- [point2]
...

Content:
[full_content]

Related Topics: [topic1, topic2, ...]
"""
```

## Best Practices

### Content Organization
1. Use clear, unique topic keys
2. Provide comprehensive definitions
3. Include relevant key concepts
4. Link related content
5. Maintain consistent formatting

### Content Updates
1. Backup before modifications
2. Validate JSON structure
3. Update aliases after changes
4. Test topic relationships
5. Verify article links

### Query Optimization
1. Use specific search terms
2. Consider alternative names
3. Check related content
4. Verify topic existence
5. Handle missing content

## Error Handling

### Common Issues
```python
try:
    result = kb.search_topic(topic)
except Exception as e:
    handle_knowledge_base_error(e)
```

### Error Types
1. FileNotFoundError: JSON file missing
2. JSONDecodeError: Invalid JSON format
3. KeyError: Missing required fields
4. ValueError: Invalid content format

## Performance Considerations

### Optimization Techniques
1. Alias caching
2. Content indexing
3. Relationship mapping
4. Response formatting
5. Error caching

### Memory Management
1. Lazy loading
2. Content pagination
3. Result caching
4. Resource cleanup
5. Memory monitoring

## Development Guidelines

### Adding New Topics
1. Follow JSON schema
2. Include all required fields
3. Add relevant aliases
4. Link related content
5. Update documentation

### Modifying Content
1. Preserve structure
2. Update relationships
3. Maintain formatting
4. Test changes
5. Update aliases

### Testing
1. Verify topic retrieval
2. Check article access
3. Test relationships
4. Validate formatting
5. Check error handling 