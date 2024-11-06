# Project Oracle Architecture

## System Overview

Project Oracle uses a multi-agent architecture powered by OpenAI's GPT-4, with async Python for efficient processing.

## Core Components

### Agent System

```curl
├── BaseAgent
│   ├── OnboardingAgent
│   ├── ResearchAgent
│   └── SearchAgent
└── Orchestrator
```

### Key Components

- **Orchestrator**: Routes messages to appropriate agents
- **BaseAgent**: Common functionality for all agents
- **Specialized Agents**: Handle specific tasks
- **UI Layer**: Gradio-based interface

## Data Flow

1. User Input → UI Layer
2. UI → Orchestrator
3. Orchestrator → Specialized Agents
4. Agents → OpenAI API
5. Response → User

## Configuration System

- YAML-based configuration
- Environment variables
- Content management

## Technical Decisions

- Async Python for scalability
- Gradio for rapid UI development
- YAML for configuration
- OpenAI GPT-4 for intelligence
