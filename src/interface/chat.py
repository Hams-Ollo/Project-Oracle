"""
Chat interface module for handling user interactions.
"""

import os
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.config.settings import EMOJIS, log_step
from src.core.workflow import create_chat_workflow

# Add project root to Python path when running directly
if __name__ == "__main__":
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.insert(0, project_root)

def display_welcome():
    """Displays the welcome message and instructions"""
    log_step('start', "Starting AI Assistant")
    print("\n🔮 AI Assistant")
    print("-" * 50)
    print("I'm your AI assistant with capabilities for:")
    print("- Knowledge Base interaction")
    print("- Web scraping tasks")
    print("- General conversations")
    print("\nType 'exit' to end the chat or 'help' for assistance.")
    print("-" * 50)

def display_help():
    """Displays help information about available commands and features"""
    log_step('info', "Displaying help information")
    print("\nI can assist you with:")
    print("1. General conversation - Chat with me as you would normally.")
    print("2. Web scraping - Provide me a URL to scrape and analyze.")
    print("3. Knowledge base queries - Ask me about topics in the knowledge base or perform searches.")
    print("\nExamples:")
    print("- Chat: 'Hello! How are you?' or 'What's your favorite color?'")
    print("- Web scraping: 'Can you scrape https://example.com for me?'")
    print("- Knowledge base: 'Tell me about onboarding processes' or 'List all available topics'")

def process_workflow_response(workflow, conversation_history, user_input):
    """
    Process user input through the workflow and return a response.
    
    Args:
        workflow: The workflow instance handling user requests.
        conversation_history: List of messages in the current conversation.
        user_input: The user-provided input string.

    Returns:
        str: The assistant's response.
    """
    try:
        # Add user message to the conversation history
        conversation_history.append(HumanMessage(content=user_input))
        
        # Process the user input through the workflow
        result = None
        for step in workflow.stream({"messages": conversation_history}):
            if "__end__" not in step:
                for key in step:
                    if 'messages' in step[key]:
                        result = step[key]['messages'][-1].content
                        conversation_history.append(step[key]['messages'][-1])
        
        return result if result else "I'm not sure how to help with that."
    except Exception as e:
        log_step('error', f"Workflow processing error: {str(e)}")
        return f"I encountered an error while processing your request: {str(e)}"

def run_chat_interface(workflow):
    """
    Runs the main chat interface loop
    
    Args:
        workflow: Compiled workflow instance
    """
    conversation_history = []
    
    display_welcome()

    while True:
        try:
            # Get user input
            user_input = input(f"\n{EMOJIS['chat']} You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                log_step('done', "Ending chat session")
                print("\nGoodbye! Have a great day! 🔮")
                break
                
            if user_input.lower() == 'help':
                display_help()
                continue
                
            if not user_input:
                continue

            log_step('think', "Processing user input...")
            
            # Process the user input and get the response
            response = process_workflow_response(workflow, conversation_history, user_input)
            print(f"\n{EMOJIS['success']} Assistant: {response}")
        
        except KeyboardInterrupt:
            log_step('done', "Chat session interrupted")
            print("\nGoodbye! Have a great day! 🔮")
            break
        except Exception as e:
            log_step('error', f"Chat interface error: {str(e)}")
            print("\nI encountered an error. Please try again.")
