#-------------------------------------------------------------------------------------#
# frontend/gradio_app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run streamlit_app.py / streamlit run frontend/streamlit_app.py / python frontend/gradio_app.py
#
# Git Commands:
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

import gradio as gr
from pathlib import Path
import sys
from typing import Dict, Any, List
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Add project root to system path
sys.path.append(str(Path(__file__).parent.parent))
from src.config.settings import FIRECRAWL_API_KEY
from src.services.web_scraper import WebScraper, create_scraping_tools
from src.services.knowledge_base import KnowledgeBase, create_knowledge_tools
from src.core.workflow import create_chat_workflow
from langchain_openai import ChatOpenAI

class GradioOracle:
    def __init__(self):
        """Initialize the Gradio interface and AI components"""
        self.messages: List = []
        self.stats = {
            'messages': 0,
            'web_pages': 0,
            'kb_queries': 0,
            'session_start': datetime.now().isoformat()
        }
        
        # Initialize AI components
        self.llm = ChatOpenAI(temperature=0.7)
        self.scraper = WebScraper(FIRECRAWL_API_KEY)
        self.scraping_tools = create_scraping_tools(self.scraper)
        self.kb = KnowledgeBase()
        self.knowledge_tools = create_knowledge_tools(self.kb)
        
        self.workflow = create_chat_workflow(
            self.llm,
            self.scraping_tools,
            self.knowledge_tools
        )
    
    def process_message(self, message: str, chat_history: List) -> str:
        """Process user message and return response"""
        try:
            self.stats['messages'] += 1
            result = None
            
            for step in self.workflow.stream({
                "messages": [HumanMessage(content=message)]
            }):
                if "__end__" not in step:
                    for key in step:
                        if 'messages' in step[key]:
                            result = step[key]['messages'][-1].content
            
            return result if result else "I'm not sure how to help with that."
        except Exception as e:
            return f"I encountered an error: {str(e)}"

    def build_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface"""
        with gr.Blocks(
            title="🔮 Project Oracle",
            theme=gr.themes.Soft(
                primary_hue="purple",
                secondary_hue="blue",
            )
        ) as interface:
            gr.Markdown(
                """
                # 🔮 Project Oracle
                
                Welcome to Project Oracle! I can help you with:
                - 💬 Natural conversations
                - 🌐 Web scraping and analysis
                - 📚 Star Wars knowledge base queries
                
                Try asking me something!
                """
            )
            
            chatbot = gr.Chatbot(
                label="Chat History",
                bubble_full_width=False,
                avatar_images=("👤", "🔮")
            )
            msg = gr.Textbox(
                label="Type your message",
                placeholder="Ask me anything...",
                scale=4
            )
            clear = gr.ClearButton([msg, chatbot])
            
            # Statistics display
            with gr.Accordion("Statistics", open=False):
                with gr.Row():
                    messages_count = gr.Number(
                        value=lambda: self.stats['messages'],
                        label="Messages"
                    )
                    web_pages_count = gr.Number(
                        value=lambda: self.stats['web_pages'],
                        label="Web Pages"
                    )
                    kb_queries_count = gr.Number(
                        value=lambda: self.stats['kb_queries'],
                        label="KB Queries"
                    )
                    session_duration = gr.Text(
                        value=lambda: f"{(datetime.now() - datetime.fromisoformat(self.stats['session_start'])).seconds // 60}m",
                        label="Session Duration"
                    )
            
            # Example queries
            gr.Examples(
                examples=[
                    "What can you tell me about Star Wars?",
                    "Can you search the web for recent AI news?",
                    "Tell me about the Jedi Order.",
                ],
                inputs=msg
            )
            
            # Handle message submission
            msg.submit(
                self.process_message,
                [msg, chatbot],
                [chatbot],
                clear_input=True
            )
            
            # Update statistics periodically
            interface.load(
                lambda: self.stats['messages'],
                None,
                messages_count,
                every=1
            )
            
        return interface

def main():
    """Main application entry point"""
    app = GradioOracle()
    interface = app.build_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_api=False
    )

if __name__ == "__main__":
    main() 