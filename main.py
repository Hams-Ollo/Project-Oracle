from typing import Annotated, Sequence, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
from langchain_core.tools import Tool
import logging
import os
from dotenv import load_dotenv
import operator
from datetime import datetime
from pathlib import Path
import re

# Setup basic logging and environment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

# Initialize LLM
llm = ChatOpenAI(temperature=0.7)  # Slightly higher temperature for more natural conversation

# Add emoji constants for logging
EMOJIS = {
    'start': '🚀',
    'chat': '💭',
    'web': '🌐',
    'route': '🔄',
    'error': '❌',
    'success': '✅',
    'info': 'ℹ️ ',
    'think': '🤔',
    'done': '🏁',
    'warn': '⚠️ '
}

def log_step(emoji: str, message: str):
    """Helper function for consistent logging"""
    print(f"\n{EMOJIS.get(emoji, 'ℹ️ ')} {message}")

def setup_scrape_directory():
    """Get or create scrape_dump directory"""
    scrape_dir = Path("scrape_dump")
    if scrape_dir.exists():
        log_step('info', "Using existing scrape_dump directory")
    else:
        scrape_dir.mkdir()
        log_step('info', "Created scrape_dump directory")
    return scrape_dir

def sanitize_filename(url: str) -> str:
    """Convert URL to a safe filename"""
    # Remove protocol and special characters
    filename = re.sub(r'https?://', '', url)
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{filename}_{timestamp}.md"

class WebScraper:
    """Web scraping tool using FireCrawl"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.scrape_dir = setup_scrape_directory()

    def save_markdown(self, content: str, url: str) -> str:
        """Save markdown content to file and return the filepath"""
        filename = sanitize_filename(url)
        filepath = self.scrape_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Content from {url}\n\n")
                f.write(content)
            log_step('success', f"Saved content to {filepath}")
            return str(filepath)
        except Exception as e:
            log_step('error', f"Failed to save content: {e}")
            return ""

    def scrape_url(self, url: str) -> str:
        """Scrape a single webpage"""
        try:
            log_step('web', f"Attempting to scrape URL: {url}")
            loader = FireCrawlLoader(
                api_key=self.api_key,
                url=url,
                mode="scrape"
            )
            log_step('think', "Loading content...")
            docs = loader.load()
            if not docs:
                log_step('warn', "No content found")
                return "No content found for this URL."
            
            log_step('success', "Content retrieved successfully")
            
            # Save the content and get the filepath
            content = docs[0].page_content
            filepath = self.save_markdown(content, url)
            
            if filepath:
                return f"""Successfully scraped and saved content!
                
                Content has been saved to: {filepath}
                
                Here's a brief summary of what I found:
                {content[:500]}...
                
                You can find the complete content in the saved file."""
            else:
                return f"Successfully scraped but failed to save content. Here's what I found:\n\n{content[:1000]}..."
            
        except Exception as e:
            log_step('error', f"Scraping failed: {str(e)}")
            return f"Failed to scrape URL: {str(e)}"

# Initialize scraper and create tools
scraper = WebScraper(FIRECRAWL_API_KEY)
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage. Input should be a valid URL.",
        func=scraper.scrape_url
    )
]

class RouteResponse(BaseModel):
    """Model for routing decisions with explanation"""
    next: Literal["FINISH", "WebScrape", "Conversation"]
    explanation: str

def create_webscrape_agent():
    """Create the web scraping agent"""
    log_step('info', "Creating web scraping agent")
    return create_react_agent(
        llm.bind(
            system_message="""You are a web scraping specialist. Your task is to:
            1. Extract the URL from the user's request
            2. Use the scrape_webpage tool to get the content
            3. The content will be saved automatically to a markdown file
            4. Provide a summary of what was found
            5. Let the user know where the full content is saved
            
            Always be clear about:
            - Whether the scraping was successful
            - Where the content was saved
            - What kind of content was found
            
            If you encounter any errors, explain them clearly.
            Be thorough but concise in your summaries."""
        ),
        scraping_tools
    )

def create_router():
    """Create an intelligent router using LLM for intent analysis"""
    def route_classifier(state):
        messages = state["messages"]
        log_step('route', "Analyzing user intent...")
        
        classification = llm.invoke(
            [
                SystemMessage(content="""You are a router that determines if a message requires web scraping.
                Return 'WebScrape' ONLY if the user explicitly requests to:
                - Scrape a website
                - Extract content from a URL
                - Analyze a webpage
                - Get information from a specific website
                
                Otherwise, return 'Conversation' for normal chat."""),
                *messages,
                HumanMessage(content="Respond with only one word: WebScrape or Conversation")
            ]
        )
        
        decision = classification.content.strip()
        log_step('info', f"Routing decision: {decision}")
        
        return {"next": "WebScrape" if decision == "WebScrape" else "Conversation"}

    return route_classifier

def webscrape_node(state):
    """Handle web scraping requests"""
    log_step('web', "Processing web scraping request")
    try:
        agent = create_webscrape_agent()
        result = agent.invoke(state)
        log_step('success', "Web scraping completed")
        
        # Handle different result formats
        if isinstance(result, dict):
            if "output" in result:
                return {"messages": [HumanMessage(content=result["output"])]}
            elif "messages" in result:
                return {"messages": [HumanMessage(content=result["messages"][-1].content)]}
        
        # Fallback for other result formats
        return {"messages": [HumanMessage(content=str(result))]}
        
    except Exception as e:
        log_step('error', f"Web scraping failed: {str(e)}")
        error_message = f"""I encountered an error while trying to scrape the website. 
        Error details: {str(e)}
        
        Please check that:
        1. The URL is valid and accessible
        2. The website allows scraping
        3. Try again or try with a different URL"""
        return {"messages": [HumanMessage(content=error_message)]}

def conversation_node(state):
    """Handle regular conversation"""
    log_step('chat', "Processing conversation")
    try:
        messages = state["messages"]
        response = llm.invoke(messages)
        log_step('success', "Generated response")
        return {"messages": [response]}
    except Exception as e:
        log_step('error', f"Conversation error: {str(e)}")
        return {"messages": [HumanMessage(content="I'm having trouble processing that. Could you rephrase?")]}

def create_chat_workflow():
    """Create the chat workflow with intelligent routing"""
    log_step('start', "Initializing chat workflow")
    
    # Define state
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        next: str

    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes with logging
    workflow.add_node("WebScrape", webscrape_node)
    log_step('info', "Added WebScrape node")
    
    workflow.add_node("Conversation", conversation_node)
    log_step('info', "Added Conversation node")
    
    workflow.add_node("router", create_router())
    log_step('info', "Added Router node")

    # Add edges
    workflow.add_edge(START, "router")
    workflow.add_edge("WebScrape", END)
    workflow.add_edge("Conversation", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "WebScrape": "WebScrape",
            "Conversation": "Conversation"
        }
    )

    log_step('success', "Chat workflow initialized")
    return workflow.compile()

def chat():
    """Run the chat interface"""
    workflow = create_chat_workflow()
    conversation_history = []
    
    # Increase recursion limit for complex scraping tasks
    config = {
        "recursion_limit": 150,  # Increased from default 25
        "timeout": 300  # 5 minutes timeout
    }
    
    log_step('start', "Starting AI Assistant")
    print("\nAI Assistant")
    print("-" * 50)
    print("I'm your AI assistant with web scraping capabilities.")
    print("Type 'exit' to end the chat or 'help' for assistance.")
    print("-" * 50)

    while True:
        try:
            user_input = input(f"\n{EMOJIS['chat']} You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                log_step('done', "Ending chat session")
                print("Goodbye! Have a great day!")
                break
                
            if user_input.lower() == 'help':
                log_step('info', "Displaying help information")
                print("\nI can help you with:")
                print("1. General conversation - just chat with me normally")
                print("2. Web scraping - ask me to get content from any webpage")
                print("\nExamples:")
                print("- Chat: 'Hello! How are you?' 'What's your favorite color?'")
                print("- Web: 'Can you scrape https://example.com for me?'")
                print("- Web: 'What's on this website: https://example.com'")
                continue
                
            if not user_input:
                continue

            log_step('think', "Processing your request...")
            
            # Add to conversation history
            conversation_history.append(HumanMessage(content=user_input))
            
            # Process through workflow with increased limits
            result = None
            for step in workflow.stream({
                "messages": [
                    SystemMessage(content="""You are a helpful AI assistant that can:
                    1. Engage in natural conversation
                    2. Analyze and extract web content when requested
                    
                    Be friendly, helpful, and engaging in your responses."""),
                    *conversation_history
                ]
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
            print("\nI encountered an error. Please try again with a smaller batch of URLs or one at a time.")

if __name__ == "__main__":
    chat()