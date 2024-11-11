# User Guide for Project Oracle

## Overview

Project Oracle is a multi-agent chat system that provides:
- General conversation capabilities
- Web content scraping and storage
- Knowledge base querying about Star Wars topics

## Getting Started

### Basic Interaction

The system provides a simple chat interface:
```bash
AI Assistant
--------------------------------------------------
I'm your AI assistant with web scraping capabilities.
Type 'exit' to end the chat or 'help' for assistance.
--------------------------------------------------

💭 You: 
```

### Basic Commands
- `help`: Display available commands and examples
- `exit` or `quit`: End the chat session

## Features

### 1. General Conversation
```bash
You: Hello, how are you today?
Assistant: Hello! I'm doing well, thank you for asking. How can I help you today?
```

### 2. Web Scraping
```bash
You: Can you scrape https://example.com?
Assistant: I'll scrape that website for you...
[Content will be saved to scrape_dump folder]
```

### 3. Knowledge Base Queries
```bash
You: What do you know about the Jedi Order?
Assistant: Let me search our knowledge base...
[Returns information about the Jedi Order]
```

## Using Web Scraping

### Basic Scraping
```bash
# Direct URL scraping
"Please scrape https://example.com"

# Content analysis request
"What's on this website: https://example.com"
```

### Viewing Results
- Scraped content is saved in the `scrape_dump` folder
- Files are named with URL and timestamp
- Content is stored in markdown format

## Accessing Knowledge Base

### Available Topics
```bash
# List all topics
"What topics do you know about?"
"List available topics"

# Search specific topic
"Tell me about the Jedi Order"
"What do you know about the Sith?"
```

### Article Retrieval
```bash
# Get specific article
"Show me the article about the Jedi Code"
"Get information about lightsabers"
```

## Best Practices

### Web Scraping
1. Provide complete URLs
2. Wait for confirmation of save
3. Check scrape_dump folder for results
4. Use for publicly accessible pages

### Knowledge Queries
1. Start with topic listing
2. Use specific topic names
3. Ask about related topics
4. Request article details

### General Usage
1. Be specific in requests
2. Check command feedback
3. Review saved content
4. Use help when needed

## Troubleshooting

### Common Issues

1. Web Scraping Errors
```bash
# Invalid URL
Error: Failed to scrape URL
Solution: Check URL format and accessibility

# Save Errors
Error: Failed to save content
Solution: Check scrape_dump folder permissions
```

2. Knowledge Base Issues
```bash
# Topic Not Found
Error: No information found for topic
Solution: Use "list topics" to see available topics

# Article Not Found
Error: No article found with title
Solution: Check article title spelling
```

### Error Messages

The system uses emoji indicators for different states:
- ❌ Error state
- ✅ Success
- ⚠️ Warning
- ℹ️ Information

## Examples

### Web Scraping Workflow
```bash
You: Scrape https://example.com
Assistant: 🌐 Attempting to scrape URL...
✅ Content saved to: scrape_dump/example_com_20240318_123456.md
```

### Knowledge Base Query
```bash
You: Tell me about the Jedi Order
Assistant: 🤔 Searching knowledge base...
✅ Found information about Jedi Order...
[Displays topic information]
```

### General Conversation
```bash
You: What can you help me with?
Assistant: I can help you with:
1. Web scraping and content analysis
2. Information about Star Wars topics
3. General conversation and questions
```

## Advanced Usage

### Combining Features
```bash
# Scrape and analyze
"Scrape this URL and tell me if it mentions Jedi"

# Knowledge and context
"Compare this website's content with what we know about Sith"
```

### Session Management
- Conversations maintain context
- History is preserved during session
- Use clear topic transitions

## Support

### Getting Help
1. Use the `help` command
2. Check error messages
3. Review saved files
4. Check documentation

### Feedback
- Clear error messages
- Operation status updates
- Save confirmations
- Processing indicators
