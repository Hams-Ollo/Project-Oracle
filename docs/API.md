# API Documentation

## Internal APIs

### BaseAgent

```python
class BaseAgent:
    async def process(message: str) -> str
    async def get_completion(messages: list) -> str
```

### Orchestrator

```python
class Orchestrator:
    async def route_message(message: str) -> Dict[str, str]
```

### Specialized Agents

#### OnboardingAgent

```python
class OnboardingAgent:
    async def process(message: str) -> str
    def load_onboarding_content() -> None
```

## Configuration

### YAML Structure

- `config.yaml`
- `onboarding_content.yaml`

## Error Handling

- Standard error responses
- Error codes and meanings
- Recovery procedures
