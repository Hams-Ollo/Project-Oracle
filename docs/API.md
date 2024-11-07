# API Documentation

## Overview

Project Oracle's API architecture consists of several key components that enable the multi-agent system to function effectively.

## Internal APIs

### BaseAgent

```python
class BaseAgent:
    """Base class for all specialized agents"""
    
    async def process(self, message: str) -> str:
        """Process incoming messages and generate responses
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The agent's response
        """
        
    async def get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from LLM
        
        Args:
            messages (List[Dict[str, str]]): Conversation history
            
        Returns:
            str: LLM completion response
        """
        
    def get_context(self, query: str) -> str:
        """Retrieve relevant documentation context
        
        Args:
            query (str): User's query
            
        Returns:
            str: Related documentation context
        """
```

### Orchestrator

```python
class Orchestrator:
    """Manages agent routing and interactions"""
    
    async def route_message(self, message: str) -> Dict[str, Any]:
        """Route messages to appropriate agents
        
        Args:
            message (str): User's input message
            
        Returns:
            Dict[str, Any]: {
                'response': str,
                'agent': str,
                'confidence': float
            }
        """
```

### Specialized Agents

#### OnboardingAgent

```python
class OnboardingAgent(BaseAgent):
    """Handles onboarding-related queries"""
    
    async def process(self, message: str) -> str:
        """Process onboarding-specific queries"""
        
    def load_onboarding_content(self) -> None:
        """Load onboarding configuration from YAML"""
```

## Configuration

### YAML Structure

#### config.yaml

```yaml
agents:
  onboarding:
    model: "gpt-4o-mini"
    temperature: 0.7
  technical:
    model: "gpt-4o-mini"
    temperature: 0.5
  process:
    model: "gpt-4o-mini"
    temperature: 0.6
```

#### onboarding_content.yaml

```yaml
skills:
  technical:
    - name: "Python"
    - name: "Git"
  processes:
    - name: "Code Review"
    - name: "Documentation"
```

## Error Handling

### Standard Error Responses

```python
{
    'error': str,           # Error description
    'error_code': int,      # Numeric error code
    'timestamp': str,       # ISO format timestamp
    'request_id': str       # Unique request identifier
}
```

### Error Codes

- 1000: Invalid input
- 1001: Agent unavailable
- 1002: Configuration error
- 1003: LLM API error
- 1004: Context retrieval error

### Recovery Procedures

1. Retry with exponential backoff
2. Fallback to default agent
3. Cache response handling
4. Error logging and monitoring

## Rate Limiting

- 10 requests per minute per user
- 1000 tokens per request
- Bulk request handling available

## Security

- API key required for all requests
- Request signing for sensitive operations
- Rate limiting per API key
- Input validation and sanitization
