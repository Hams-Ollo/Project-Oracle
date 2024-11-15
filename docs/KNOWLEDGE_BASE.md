# Knowledge Base Documentation

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
   ├── knowledge_base/
   │   ├── knowledge_base.json
   │   ├── markdown/
   │   │   └── *.md files
   │   └── vectors/
   │       └── chroma.db
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
                "title": "Article title",
                "summary": "Brief summary",
                "content": "Full content"
            }
        }
    }
}
```

### 2. Markdown Files

- Place markdown files in the `/knowledge_base/markdown/` directory
- Use frontmatter for metadata
- Include clear headings
- Add tags for better searchability
