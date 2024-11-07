#-------------------------------------------------------------------------------------#
# MAIN.PY
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run app.py 
#-------------------------------------------------------------------------------------#
# Git Version Control Commands:
# 1. Initialize repository -> git init
# 2. Add files to staging -> git add .
# 3. Commit changes -> git commit -m "your message"
# 4. Create new branch -> git checkout -b branch-name
# 5. Switch branches -> git checkout branch-name
# 6. Push to remote -> git push -u origin branch-name
# 7. Pull latest changes -> git pull origin branch-name
# 8. Check status -> git status
# 9. View commit history -> git log
#-------------------------------------------------------------------------------------#

# IMPORTS
import os
from dotenv import load_dotenv
from swarm import Swarm, Agent
import openai
from utils.knowledge_base import KnowledgeBase
from typing import Dict, List, Optional

# Load environment variables and configure settings
load_dotenv()
print("[INFO] Environment variables loaded successfully")

# Configure OpenAI globally
openai.api_key = os.getenv("OPENAI_API_KEY")
print("[CONFIG] OpenAI API configured globally")

def format_debug_info(message, level="INFO"):
    """Format debug information with consistent styling"""
    prefix = {
        "INFO": "\033[94m[INFO]\033[0m",    # Blue
        "DEBUG": "\033[92m[DEBUG]\033[0m",   # Green
        "ERROR": "\033[91m[ERROR]\033[0m",   # Red
        "SYSTEM": "\033[95m[SYSTEM]\033[0m", # Purple
        "TRANSFER": "\033[93m[TRANSFER]\033[0m", # Yellow
        "ASSISTANT": "\033[96m" # Cyan for bot responses
    }
    return f"{prefix.get(level, '[LOG]')} {message}"

# Create a wrapper class to handle documentation functionality
class AgentWithDocs:
    def __init__(self, agent: Agent, knowledge_base: KnowledgeBase):
        self.agent = agent
        self.kb = knowledge_base
        
    def get_context_from_docs(self, query: str) -> str:
        """Retrieve relevant information from knowledge base"""
        results = self.kb.search(query)
        return self.kb.format_response(results)

    @property
    def name(self):
        return self.agent.name

    @property
    def functions(self):
        return self.agent.functions

    @functions.setter
    def functions(self, value):
        self.agent.functions = value

def main():
    """
    Main function that initializes and runs the multi-agent conversation system.
    """
    # Print API key for debugging (first 5 chars)
    print(f"[DEBUG] Using API key starting with: {os.getenv('OPENAI_API_KEY')[:5]}...")
    
    # Initialize swarm client for managing agent interactions
    swarm = Swarm()
    print("[INIT] Swarm client initialized")
    
    # Initialize KnowledgeBase instead of DocumentationLoader
    kb = KnowledgeBase()
    print("[INIT] Knowledge base initialized")
    
    # Create specialized agents with knowledge base
    onboarding_agent = AgentWithDocs(
        agent=Agent(
            name="Onboarding Specialist",
            instructions="""You are an onboarding specialist who helps new team members understand their role and required skills.
            When answering questions, use the provided documentation context to give accurate, specific answers about this project.""",
            model="gpt-4o-mini"
        ),
        knowledge_base=kb
    )
    
    technical_agent = AgentWithDocs(
        agent=Agent(
            name="Technical Advisor",
            instructions="""You are a technical advisor who provides detailed technical guidance and best practices.
            Use the provided documentation context to give specific, accurate technical information about this project.""",
            model="gpt-4o-mini"
        ),
        knowledge_base=kb
    )
    
    process_agent = AgentWithDocs(
        agent=Agent(
            name="Process Guide",
            instructions="""You are a process guide who explains workflows and organizational procedures.
            Reference the provided documentation context when explaining processes specific to this project.""",
            model="gpt-4o-mini"
        ),
        knowledge_base=kb
    )
    
    print("[SETUP] All agents initialized successfully")
    
    # Define handoff functions for agent transitions
    def transfer_to_technical():
        """Handles transition to technical advisor agent"""
        print("[TRANSFER] Initiating handoff to Technical Advisor")
        return technical_agent.agent  # Return the underlying Agent object

    def transfer_to_process():
        """Handles transition to process guide agent"""
        print("[TRANSFER] Initiating handoff to Process Guide")
        return process_agent.agent  # Return the underlying Agent object
    
    # Configure agent routing capabilities
    onboarding_agent.functions = [transfer_to_technical, transfer_to_process]
    print("[CONFIG] Agent transfer functions configured")
    
    # Initialize conversation state
    messages = []
    current_agent = onboarding_agent
    
    print(format_debug_info("Welcome to the Team Assistant! Type 'quit' to exit.", "SYSTEM"))
    print(format_debug_info(f"Currently speaking with: {current_agent.name}", "SYSTEM"))
    print("\n" + "="*80 + "\n") # Add visual separator
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\033[1mYou:\033[0m ") # Bold "You:" prompt
        
        if user_input.lower() == 'quit':
            print(format_debug_info("Terminating conversation...", "SYSTEM"))
            break
            
        # Track conversation history
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get relevant documentation context
            doc_context = current_agent.get_context_from_docs(user_input)
            
            # Add documentation context to the conversation
            context_message = {
                "role": "system",
                "content": f"Use this documentation context to inform your response: {doc_context}"
            } if doc_context else None
            
            # Create messages list with context
            messages_with_context = messages.copy()
            if context_message:
                messages_with_context.insert(-1, context_message)
            
            # Process conversation through swarm with context
            if os.getenv("DEBUG_MODE"):
                print(format_debug_info("Generating response...", "DEBUG"))
                
            response = swarm.run(
                agent=current_agent.agent,  # Use the underlying Agent object
                messages=messages_with_context,
                context_variables={"user_name": "New Team Member"},
                debug=os.getenv("DEBUG_MODE", "false").lower() == "true"
            )
            
            # Handle response and update conversation
            if isinstance(response, dict):
                if "messages" in response:
                    for message in response["messages"]:
                        if message.get("role") == "assistant":
                            content = message.get('content', '')
                            # Color only the content portion
                            message['content'] = f"\033[96m{content}\033[0m"
                            print(f"\n\033[1m{current_agent.name}:\033[0m {message}")
                            messages.append(message)
                if "next_agent" in response:
                    current_agent = response["next_agent"]
                    print(format_debug_info(f"Successfully transferred to {current_agent.name}", "TRANSFER"))
            else:
                # Color only the response content
                colored_response = f"\033[96m{response}\033[0m"
                print(f"\n\033[1m{current_agent.name}:\033[0m {colored_response}")
                messages.append({"role": "assistant", "content": str(response)})
            
            print("\n" + "-"*80 + "\n") # Add visual separator between exchanges
                
        except Exception as e:
            print(format_debug_info(f"An error occurred: {e}", "ERROR"))
            print(format_debug_info("Please try again.", "SYSTEM"))

if __name__ == "__main__":
    main()
