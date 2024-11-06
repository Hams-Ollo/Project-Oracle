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

def main():
    """
    Main function that initializes and runs the multi-agent conversation system.
    Handles agent creation, message routing, and user interactions.
    """
    # Print API key for debugging (first 5 chars)
    print(f"[DEBUG] Using API key starting with: {os.getenv('OPENAI_API_KEY')[:5]}...")
    
    # Initialize swarm client for managing agent interactions
    swarm = Swarm()
    print("[INIT] Swarm client initialized")
    
    # Create specialized agents with specific roles and responsibilities
    print("[SETUP] Initializing specialized agents...")
    
    onboarding_agent = Agent(
        name="Onboarding Specialist",
        instructions="You are an onboarding specialist who helps new team members understand their role and required skills.",
        model="gpt-4o-mini"  # Updated model
    )
    
    technical_agent = Agent(
        name="Technical Advisor",
        instructions="You are a technical advisor who provides detailed technical guidance and best practices.",
        model="gpt-4o-mini"  # Updated model
    )
    
    process_agent = Agent(
        name="Process Guide",
        instructions="You are a process guide who explains workflows and organizational procedures.",
        model="gpt-4o-mini"  # Updated model
    )
    print("[SETUP] All agents initialized successfully")
    
    # Define handoff functions for agent transitions
    def transfer_to_technical():
        """Handles transition to technical advisor agent"""
        print("[TRANSFER] Initiating handoff to Technical Advisor")
        return technical_agent

    def transfer_to_process():
        """Handles transition to process guide agent"""
        print("[TRANSFER] Initiating handoff to Process Guide")
        return process_agent
    
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
            # Process conversation through swarm
            if os.getenv("DEBUG_MODE"):
                print(format_debug_info("Generating response...", "DEBUG"))
                
            response = swarm.run(
                agent=current_agent,
                messages=messages,
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
