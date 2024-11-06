#-------------------------------------------------------------------------------------#
# TEST.PY
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
import os
from dotenv import load_dotenv
from swarm import Swarm, Agent
import openai

# Load environment variables
load_dotenv()

# Configure OpenAI globally
openai.api_key = os.getenv("OPENAI_API_KEY")

def main():
    # Print API key for debugging (first 5 chars)
    print(f"Using API key starting with: {os.getenv('OPENAI_API_KEY')[:5]}...")
    
    # Initialize swarm client (without api_key parameter)
    swarm = Swarm()
    
    # Create specialized agents
    onboarding_agent = Agent(
        name="Onboarding Specialist",
        instructions="You are an onboarding specialist who helps new team members understand their role and required skills.",
        model="gpt-3.5-turbo"  # Using standard OpenAI model name
    )
    
    technical_agent = Agent(
        name="Technical Advisor",
        instructions="You are a technical advisor who provides detailed technical guidance and best practices.",
        model="gpt-3.5-turbo"
    )
    
    process_agent = Agent(
        name="Process Guide",
        instructions="You are a process guide who explains workflows and organizational procedures.",
        model="gpt-3.5-turbo"
    )
    
    # Define handoff functions
    def transfer_to_technical():
        return technical_agent

    def transfer_to_process():
        return process_agent
    
    # Add transfer functions to onboarding agent
    onboarding_agent.functions = [transfer_to_technical, transfer_to_process]
    
    # Example conversation
    messages = [
        {"role": "user", "content": "Hi, I'm new here and need help understanding my role."}
    ]
    
    try:
        # Run the conversation
        response = swarm.run(
            agent=onboarding_agent,
            messages=messages,
            context_variables={"user_name": "New Team Member"},
            debug=True
        )
        
        # Print the conversation
        for message in response.messages:
            sender = message.get("sender", "User")
            content = message.get("content", "")
            print(f"\n{sender}: {content}")
            
    except Exception as e:
        print(f"Error running swarm: {e}")

if __name__ == "__main__":
    main()
