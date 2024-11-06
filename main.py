import os
from dotenv import load_dotenv
import openai
from src.ui.gradio_interface import ChatInterface

def main():
    # Load environment variables
    load_dotenv()
    
    # Configure OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Create and launch interface
    chat_interface = ChatInterface()
    interface = chat_interface.create_interface()
    interface.launch(server_name="0.0.0.0", server_port=7860)

if __name__ == "__main__":
    main() 