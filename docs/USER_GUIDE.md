# User Guide for Project Oracle

## Overview

Project Oracle is an AI-powered assistant that helps users understand and work with the project through natural conversation. This guide will help you get the most out of your interactions with the system.

## Getting Started

### First-Time Setup

1. **System Access**

```bash
# Start the application
python main.py

# The system will display:
[INFO] Environment variables loaded successfully
[CONFIG] OpenAI API configured globally
[INIT] Knowledge base initialized
[SETUP] All agents initialized successfully
```

2. **Initial Interaction**

- Type your questions or requests naturally
- The system will respond with relevant information
- Commands are case-insensitive
- Type 'quit' to exit the system

### Basic Commands

```bash
# Get project information
"Tell me about Project Oracle"
"What is this project?"

# Get setup help
"How do I set up the project?"
"What are the installation steps?"

# Get technical information
"Explain the architecture"
"How does the agent system work?"
```

## Working with Agents

### Available Agents

1. **Onboarding Specialist**
   - New user guidance
   - Project introduction
   - Setup assistance
   - Basic workflows

2. **Technical Advisor**
   - Technical documentation
   - Architecture details
   - Implementation guidance
   - Best practices

3. **Process Guide**
   - Workflow procedures
   - Development processes
   - Guidelines and standards
   - Project management

### Agent Interaction

```bash
# The system automatically routes your query to the appropriate agent
You: How do I set up my development environment?
[Onboarding Specialist will respond]

You: Explain the system architecture
[Technical Advisor will respond]

You: What's the git workflow?
[Process Guide will respond]
```

## Features

### Documentation Search

- Agents can access project documentation
- Responses include relevant documentation context
- Documentation is categorized by topic

Example:

```bash
You: "How does the knowledge base work?"
[System will provide relevant technical documentation]
```

### Context-Aware Responses

- System maintains conversation context
- References previous messages when relevant
- Provides coherent multi-turn conversations

Example:

```bash
You: "Tell me about the agents"
[System explains agents]
You: "How do they communicate?"
[System understands context and explains agent communication]
```

### Agent Handoff

- Automatic transfer to appropriate specialist
- Seamless conversation continuation
- Context preservation during transfers

## Tips & Tricks

### Effective Queries

1. **Be Specific**

```bash
# Less effective:
"How does it work?"

# More effective:
"How does the agent handoff system work?"
```

2. **Use Keywords**

```bash
# For technical information:
"architecture", "implementation", "technical"

# For process information:
"workflow", "process", "procedure"

# For setup help:
"setup", "installation", "configuration"
```

### Troubleshooting

Common Issues and Solutions:

1. **Unclear Responses**

```bash
# Rephrase your question
Original: "How does it handle docs?"
Better: "Explain how the system manages documentation retrieval"
```

2. **Wrong Agent**

```bash
# Explicitly request specific expertise
"Can a technical advisor explain the architecture?"
"I need onboarding help with setup"
```

3. **Missing Context**

```bash
# Provide more context in your query
"How do I contribute to the project's documentation system?"
```

## Advanced Usage

### Debug Mode

```bash
# Enable debug mode in .env
DEBUG_MODE=true

# You'll see additional information:
[DEBUG] Generating response...
[DEBUG] Retrieved context from knowledge base...
```

### Documentation Categories

```bash
# Access specific documentation types:
"Show me the security guidelines"
"What are the deployment procedures?"
"Explain the testing requirements"
```

## Best Practices

1. **Session Management**
   - Start with clear objectives
   - Follow logical conversation flow
   - Use complete sentences
   - Review important information

2. **Documentation Access**
   - Request specific documents
   - Ask for clarification when needed
   - Use documentation keywords
   - Reference specific sections

3. **Problem Resolution**
   - Describe issues clearly
   - Provide relevant context
   - Follow suggested solutions
   - Report unexpected behavior

## Support

### Getting Help

- Review this user guide
- Check the FAQ section
- Examine relevant documentation
- Ask the appropriate agent

### Feedback

- Report issues on GitHub
- Suggest improvements
- Share success stories
- Contribute to documentation
