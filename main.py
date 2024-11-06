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
import openai
from src.ui.gradio_interface import ChatInterface

# MAIN FUNCTION
def main():
    # Load environment variables
    load_dotenv()
    
    # Configure OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Create and launch interface
    chat_interface = ChatInterface()
    interface = chat_interface.create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860)

# RUN MAIN FUNCTION
if __name__ == "__main__":
    main() 