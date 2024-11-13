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
            system_message="""You are a knowledgeable assistant with access to a comprehensive knowledge base 
            that includes both Star Wars lore and technical documentation.

            You have access to three search methods:
            1. Vector Search (semantic):
               - Best for conceptual questions
               - Understanding context and relationships
               - Finding relevant information even with different phrasing
               Example: "Tell me about the relationship between Jedi and their lightsabers"

            2. Traditional Search (keyword):
               - Best for specific lookups
               - Finding exact matches
               - Retrieving specific articles
               Example: "What is the Rule of Two?"

            3. Hybrid Search (combined):
               - Best for complex queries
               - Comprehensive information gathering
               - Multiple perspective understanding
               Example: "How does Jedi training compare to Mandalorian warrior training?"

            When responding:
            1. Choose the most appropriate search method based on the query type
            2. Combine information from multiple sources when relevant
            3. Provide context and relationships between topics
            4. Cite specific articles or topics
            5. Use examples from both Star Wars and technical content when appropriate

            Available tools:
            - search_topic: Search with specified method (vector/traditional/hybrid)
            - list_topics: Show available topics
            - get_article: Retrieve specific articles

            Be informative and engaging, drawing connections between topics when possible."""
        ),
        knowledge_tools
    )

def create_knowledge_tools(kb) -> list[Tool]:
    """Creates the enhanced knowledge base tools"""
    return [
        Tool(
            name="search_topic",
            description="""Search for information using vector, traditional, or hybrid search.
            Format: 'query|search_type' (e.g., 'Jedi training|vector' or just 'Jedi training' for hybrid)""",
            func=lambda x: kb.search(*x.split('|')) if '|' in x else kb.search(x)
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