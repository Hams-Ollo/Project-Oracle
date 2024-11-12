"""
Agent creation and configuration module.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from src.config.settings import log_step

def create_webscrape_agent(llm: ChatOpenAI, scraping_tools: list[Tool]):
    """
    Creates and configures the web scraping specialist agent
    
    This agent is responsible for:
    1. Understanding URL extraction from user queries
    2. Managing the web scraping process
    3. Saving and reporting results
    
    Args:
        llm: Language model instance
        scraping_tools: List of web scraping tools
    
    Returns:
        Agent: Configured web scraping agent
    """
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

def create_knowledge_agent(llm: ChatOpenAI, knowledge_tools: list[Tool]):
    """
    Creates and configures the knowledge base specialist agent
    
    This agent is responsible for:
    1. Understanding user queries about stored information
    2. Searching and retrieving relevant data
    3. Presenting information in a structured format
    
    Args:
        llm: Language model instance
        knowledge_tools: List of knowledge base tools
    
    Returns:
        Agent: Configured knowledge base agent
    """
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