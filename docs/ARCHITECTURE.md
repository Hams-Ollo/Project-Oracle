# Project Oracle Architecture

## System Overview

Project Oracle is a multi-agent chatbot system powered by OpenAI's GPT models, featuring RAG (Retrieval-Augmented Generation) capabilities and an async Python architecture for efficient processing.

## Core Components

### Agent System

```curl
project_oracle/
├── main.py                 # Application entry point
├── utils/
│   ├── __init__.py
│   ├── knowledge_base.py   # Documentation retrieval system
│   └── doc_loader.py       # Legacy documentation loader
├── agents/
│   ├── base_agent.py      # Base agent functionality
│   └── specialized/
│       ├── onboarding_agent.py
│       ├── technical_agent.py
│       └── process_agent.py
└── config/
    ├── config.yaml        # System configuration
    └── onboarding_content.yaml
```

### Key Components

#### 1. AgentWithDocs Wrapper

- Combines agent functionality with documentation access
- Manages knowledge base integration
- Handles context retrieval and formatting

#### 2. Knowledge Base

- JSON-based documentation storage
- Flexible search functionality
- Category-based information organization
- Structured response formatting

#### 3. Agent System

- **Base Agent**: Common agent functionality
- **Specialized Agents**:
  - Onboarding Specialist: New user assistance
  - Technical Advisor: Technical guidance
  - Process Guide: Workflow assistance
- **Agent Transfer System**: Dynamic agent switching

#### 4. Swarm Orchestration

- Message routing
- Agent coordination
- Context management
- Response handling

## Data Flow

1. **Input Processing**

   ```curl
   User Input → AgentWithDocs → Knowledge Base Query → Context Retrieval
   ```

2. **Agent Processing**

   ```curl
   Context + Query → Current Agent → LLM Processing → Response Generation
   ```

3. **Response Flow**

   ```curl
   Agent Response → Format Processing → User Display
   ```

## Technical Implementation

### 1. Message Processing

```python
messages_with_context = messages.copy()
if context_message:
    messages_with_context.insert(-1, context_message)
```

### 2. Agent Handoff

```python
if "next_agent" in response:
    current_agent = response["next_agent"]
```

### 3. Context Integration

```python
context_message = {
    "role": "system",
    "content": f"Use this documentation context to inform your response: {doc_context}"
}
```

## Configuration System

### Environment Variables

- OPENAI_API_KEY: API authentication
- DEBUG_MODE: Debug logging toggle

### YAML Configuration

```yaml
agents:
  onboarding:
    model: "gpt-4o-mini"
    temperature: 0.7
```

## Design Decisions

### 1. Knowledge Base Implementation

- **Choice**: JSON-based storage
- **Rationale**:

  - Easy to maintain and update
  - Fast access and searching
  - Structured data organization
  - Simple integration with Python

### 2. Agent Architecture

- **Choice**: Wrapper-based design
- **Rationale**:
  - Clean separation of concerns
  - Easy to extend functionality
  - Maintains compatibility with base agents

### 3. Context Management

- **Choice**: System message injection
- **Rationale**:
  - Preserves conversation flow
  - Allows for dynamic context updates
  - Maintains LLM context window efficiency

## Performance Considerations

- Async message processing
- Context caching capabilities
- Efficient knowledge base searches
- Response formatting optimization

## Future Enhancements

1. Database integration for larger knowledge bases
2. Real-time documentation updates
3. Enhanced agent specialization
4. Advanced context management
5. UI implementation for better interaction

## Security Measures

- API key protection
- Input validation
- Rate limiting
- Error handling
