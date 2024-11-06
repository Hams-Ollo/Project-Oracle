# Project Oracle (Alpha Release v0.1.0)

## Overview

Project Oracle is an AI-powered educational onboarding assistant that helps new user's or team members understand organizational processes and required skills. Built with async Python and OpenAI's GPT-4o, it provides an interactive chat interface for personalized onboarding guidance.

## 🌟 Current Features

- **Onboarding Agent**: Specialized agent for handling onboarding-related queries
- **Skill Assessment**: Intelligent analysis of skill requirements and learning paths
- **Process Guidance**: Clear explanation of team workflows and development processes
- **Interactive Interface**: User-friendly chat interface built with Gradio
- **Configurable Content**: YAML-based configuration for easy content updates
- **Async Architecture**: Efficient handling of chat interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- Basic understanding of YAML for content configuration

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Hams-Ollo/Project-Oracle.git  
   cd project_oracle
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

### Usage

1. Start the application:

   ```bash
   python main.py
   ```

2. Access the chat interface at `http://localhost:7860`

3. Begin interacting with the onboarding assistant by asking questions about:
   - Required technical skills
   - Team processes
   - Development workflows
   - Company policies

## 📝 Configuration

### Customizing Onboarding Content

Edit `config/onboarding_content.yaml` to modify:

- Technical skills requirements
- Soft skills expectations
- Development processes
- Team workflows

Example:
