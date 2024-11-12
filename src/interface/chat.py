"""
Chat interface module for handling user interactions.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path when running directly
if __name__ == "__main__":
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.insert(0, project_root)

from langchain_core.messages import HumanMessage
from src.config.settings import EMOJIS, log_step

def display_welcome():
    """Displays the welcome message and instructions"""
    log_step('start', "Starting AI Assistant")
    print("\nAI Assistant")
    print("-" * 50)
    print("I'm your AI assistant with web scraping capabilities.")
    print("Type 'exit' to end the chat or 'help' for assistance.")
    print("-" * 50)

def display_help():
    """Displays help information about available commands and features"""
    log_step('info', "Displaying help information")
    print("\nI can help you with:")
    print("1. General conversation - just chat with me normally")
    print("2. Web scraping - ask me to get content from any webpage")
    print("3. Knowledge base queries - ask about topics in our database")
    print("\nExamples:")
    print("- Chat: 'Hello! How are you?' 'What's your favorite color?'")
    print("- Web: 'Can you scrape https://example.com for me?'")
    print("- Knowledge: 'What do you know about the Jedi Order?'")
    print("- Knowledge: 'Tell me about the Sith'")
    print("- Knowledge: 'List all available topics'")

def run_chat_interface(workflow):
    """
    Runs the main chat interface loop
    
    Args:
        workflow: Compiled workflow instance
    """
    conversation_history = []
    
    # Configuration for workflow execution
    config = {
        "recursion_limit": 150,  # Increased from default 25
        "timeout": 300  # 5 minutes timeout
    }
    
    display_welcome()

    while True:
        try:
            user_input = input(f"\n{EMOJIS['chat']} You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                log_step('done', "Ending chat session")
                print("Goodbye! Have a great day!")
                break
                
            if user_input.lower() == 'help':
                display_help()
                continue
                
            if not user_input:
                continue

            log_step('think', "Processing your request...")
            
            # Add to conversation history
            conversation_history.append(HumanMessage(content=user_input))
            
            # Process through workflow with increased limits
            result = None
            for step in workflow.stream({
                "messages": conversation_history
            }, config=config):
                if "__end__" not in step:
                    for key in step:
                        if 'messages' in step[key]:
                            result = step[key]['messages'][-1].content
                            conversation_history.append(step[key]['messages'][-1])

            print(f"\n{EMOJIS['success']} Assistant:", result if result else "I'm not sure how to help with that.")
            
        except KeyboardInterrupt:
            log_step('done', "Chat session interrupted")
            print("\nGoodbye! Have a great day!")
            break
        except Exception as e:
            log_step('error', f"Error: {str(e)}")
            print("\nI encountered an error. Please try again.") 