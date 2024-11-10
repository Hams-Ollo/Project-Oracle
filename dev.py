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
import json

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

class KnowledgeBase:
    """Knowledge base management and querying"""
    def __init__(self, json_path: str = "knowledge_base.json"):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # Create topic aliases and keywords for better matching
            self._create_topic_mappings()
            log_step('success', f"Knowledge base loaded successfully with {len(self.data['topics'])} topics and {len(self.data['articles'])} articles")
            log_step('info', f"Available topics: {list(self.data['topics'].keys())}")
        except Exception as e:
            log_step('error', f"Failed to load knowledge base: {e}")
            self.data = {"topics": {}, "articles": {}}
            self.topic_aliases = {}
            self.article_aliases = {}

    def _create_topic_mappings(self):
        """Create mappings for flexible topic matching"""
        self.topic_aliases = {}
        self.article_aliases = {}
        
        # Create topic aliases
        for topic_key in self.data["topics"]:
            # Add the original key
            self.topic_aliases[topic_key.lower()] = topic_key
            # Add without underscores
            self.topic_aliases[topic_key.lower().replace('_', ' ')] = topic_key
            # Add key concepts as aliases
            for concept in self.data["topics"][topic_key].get("key_concepts", []):
                self.topic_aliases[concept.lower()] = topic_key
            # Add important figures as context
            for figure in self.data["topics"][topic_key].get("important_figures", []):
                self.topic_aliases[figure.lower()] = topic_key

        # Create article aliases
        for article_key in self.data["articles"]:
            # Add the original key
            self.article_aliases[article_key.lower()] = article_key
            # Add without underscores
            self.article_aliases[article_key.lower().replace('_', ' ')] = article_key
            # Add title as alias
            title = self.data["articles"][article_key].get("title", "").lower()
            self.article_aliases[title] = article_key
            # Add key points as context
            for point in self.data["articles"][article_key].get("key_points", []):
                key_terms = ' '.join(point.split()[:3]).lower()  # First three words of each key point
                self.article_aliases[key_terms] = article_key

    def _find_best_topic_match(self, query: str) -> str:
        """Find the best matching topic for a query"""
        query = query.lower()
        
        # Direct match
        if query in self.topic_aliases:
            return self.topic_aliases[query]
        
        # Partial matches
        matches = []
        for alias, topic in self.topic_aliases.items():
            if query in alias or alias in query:
                matches.append(topic)
        
        return matches[0] if matches else None

    def search_topic(self, topic: str) -> str:
        """Search for information about a specific topic with flexible matching"""
        log_step('info', f"Searching for topic: {topic}")
        
        matched_topic = self._find_best_topic_match(topic)
        if matched_topic:
            content = self.data["topics"][matched_topic]
            log_step('success', f"Found topic: {matched_topic}")
            
            # Get related topics
            related_topics = []
            for other_topic in self.data["topics"]:
                if other_topic != matched_topic:
                    if any(concept in content.get("key_concepts", []) 
                          for concept in self.data["topics"][other_topic].get("key_concepts", [])):
                        related_topics.append(other_topic)

            return f"""Topic: {matched_topic}

Definition: {content.get('definition', 'No definition available')}

Key Concepts: {', '.join(content.get('key_concepts', []))}

Important Figures: {', '.join(content.get('important_figures', []))}

Cultural Significance: {content.get('cultural_significance', 'No information available')}

Related Topics: {', '.join(related_topics) if related_topics else 'None found'}

Related Articles: {self._find_related_articles(matched_topic)}"""
        
        log_step('warn', f"No information found for topic: {topic}")
        return f"No information found for topic: {topic}. Available topics: {', '.join(self.data['topics'].keys())}"

    def _find_related_articles(self, topic: str) -> str:
        """Find articles related to a topic"""
        related = []
        topic_lower = topic.lower()
        
        for article_key, article in self.data["articles"].items():
            content = article.get("content", "").lower()
            if topic_lower in content or any(kw in content for kw in self.data["topics"][topic].get("key_concepts", [])):
                related.append(article["title"])
        
        return ', '.join(related) if related else 'None found'

    def get_article(self, title: str) -> str:
        """Get a specific article with flexible matching"""
        title = title.lower()
        
        # Direct match
        if title in self.article_aliases:
            article_key = self.article_aliases[title]
            article = self.data["articles"][article_key]
            log_step('success', f"Found article: {article['title']}")
            
            return f"""Article: {article.get('title', 'Untitled')}

Summary: {article.get('summary', 'No summary available')}

Key Points:
{chr(10).join('- ' + point for point in article.get('key_points', []))}

Content:
{article.get('content', 'No content available')}

Related Topics: {self._find_related_topics(article_key)}"""
        
        # Partial matches
        for alias, key in self.article_aliases.items():
            if title in alias or alias in title:
                article = self.data["articles"][key]
                log_step('success', f"Found similar article: {article['title']}")
                return self.get_article(key)
        
        log_step('warn', f"No article found with title: {title}")
        return f"No article found with title: {title}. Try one of these: {', '.join(article['title'] for article in self.data['articles'].values())}"

    def _find_related_topics(self, article_key: str) -> str:
        """Find topics related to an article"""
        related = []
        article_content = self.data["articles"][article_key].get("content", "").lower()
        
        for topic_key, topic in self.data["topics"].items():
            if (topic_key.lower() in article_content or 
                any(concept.lower() in article_content for concept in topic.get("key_concepts", []))):
                related.append(topic_key)
        
        return ', '.join(related) if related else 'None found'

    def list_topics(self) -> str:
        """List all available topics with their definitions"""
        if not self.data["topics"]:
            return "No topics available in the knowledge base."
        
        topic_list = []
        for topic, content in self.data["topics"].items():
            definition = content.get("definition", "No definition available")
            # Take first sentence of definition for brevity
            short_def = definition.split('. ')[0]
            topic_list.append(f"- {topic}: {short_def}")
        
        return "Available Topics:\n" + "\n".join(topic_list)

    def list_articles(self) -> str:
        """List all available articles with their summaries"""
        if not self.data["articles"]:
            return "No articles available in the knowledge base."
        
        article_list = []
        for article_key, article in self.data["articles"].items():
            title = article.get("title", article_key)
            summary = article.get("summary", "No summary available")
            article_list.append(f"- {title}: {summary}")
        
        return "Available Articles:\n" + "\n".join(article_list)

# Initialize scraper and create tools
scraper = WebScraper(FIRECRAWL_API_KEY)
scraping_tools = [
    Tool(
        name="scrape_webpage",
        description="Scrape content from a webpage. Input should be a valid URL.",
        func=scraper.scrape_url
    )
]

# Initialize knowledge base and create tools
kb = KnowledgeBase()
knowledge_tools = [
    Tool(
        name="search_topic",
        description="Search for information about a specific topic in the knowledge base",
        func=kb.search_topic
    ),
    Tool(
        name="list_topics",
        description="List all available topics in the knowledge base",
        func=kb.list_topics
    ),
    Tool(
        name="get_article",
        description="Get a specific article by its title",
        func=kb.get_article
    )
]

class RouteResponse(BaseModel):
    """Model for routing decisions"""
    next: Literal["FINISH", "WebScrape", "Knowledge", "Conversation"]

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

def create_knowledge_agent():
    """Create the knowledge base agent"""
    log_step('info', "Creating knowledge base agent")
    return create_react_agent(
        llm.bind(
            system_message="""You are a knowledge base specialist with access to information about Star Wars topics.
            
            When asked about available topics or contents:
            1. ALWAYS use the list_topics tool first
            2. Present the results clearly
            
            When asked about specific topics:
            1. Use search_topic to get detailed information
            2. Use get_article for related articles
            
            Available tools:
            - list_topics: Shows all available topics (use this for general inquiries)
            - search_topic: Gets detailed information about a specific topic
            - get_article: Retrieves specific articles
            
            Be direct and efficient in your responses."""
        ),
        knowledge_tools
    )

def create_router():
    """Create an intelligent router using LLM for intent analysis"""
    def route_classifier(state):
        messages = state["messages"]
        log_step('route', "Analyzing user intent...")
        
        classification = llm.invoke(
            [
                SystemMessage(content="""You are a router that determines how to handle user requests.
                
                Return 'Knowledge' if the user:
                - Asks what information is available
                - Asks about the knowledge base contents
                - Asks about any Star Wars topic
                - Requests to list or see available topics
                
                Return 'WebScrape' if the user:
                - Mentions a URL
                - Asks to scrape or extract from a website
                
                Return 'Conversation' for:
                - General chat
                - Greetings
                - Other queries
                
                Be precise in routing knowledge base queries."""),
                *messages,
                HumanMessage(content="Respond with only one word: WebScrape, Knowledge, or Conversation")
            ]
        )
        
        decision = classification.content.strip()
        log_step('info', f"Routing decision: {decision}")
        
        return {"next": decision}

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

def knowledge_node(state):
    """Handle knowledge base queries"""
    log_step('info', "Processing knowledge base query")
    try:
        agent = create_knowledge_agent()
        result = agent.invoke(state)
        log_step('success', "Knowledge retrieval completed")
        
        if isinstance(result, dict):
            if "output" in result:
                return {"messages": [HumanMessage(content=result["output"])]}
            elif "messages" in result:
                return {"messages": [HumanMessage(content=result["messages"][-1].content)]}
        
        return {"messages": [HumanMessage(content=str(result))]}
        
    except Exception as e:
        log_step('error', f"Knowledge retrieval failed: {str(e)}")
        return {"messages": [HumanMessage(content=f"I encountered an error while searching the knowledge base: {str(e)}")]}

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
    
    workflow.add_node("Knowledge", knowledge_node)
    log_step('info', "Added Knowledge node")
    
    workflow.add_node("Conversation", conversation_node)
    log_step('info', "Added Conversation node")
    
    workflow.add_node("router", create_router())
    log_step('info', "Added Router node")

    # Add edges
    workflow.add_edge(START, "router")
    workflow.add_edge("WebScrape", END)
    workflow.add_edge("Knowledge", END)
    workflow.add_edge("Conversation", END)

    # Add conditional edges
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next"],
        {
            "WebScrape": "WebScrape",
            "Knowledge": "Knowledge",
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
                print("3. Knowledge base queries - ask about topics in our database")
                print("\nExamples:")
                print("- Chat: 'Hello! How are you?' 'What's your favorite color?'")
                print("- Web: 'Can you scrape https://example.com for me?'")
                print("- Knowledge: 'What do you know about the Jedi Order?'")
                print("- Knowledge: 'Tell me about the Sith'")
                print("- Knowledge: 'List all available topics'")
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