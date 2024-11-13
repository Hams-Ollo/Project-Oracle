"""
Workflow creation and routing module.
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
import operator

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import ChatOpenAI

from src.config.settings import log_step
from src.core.agents import create_webscrape_agent, create_knowledge_agent

class AgentState(TypedDict):
    """Type definition for agent state"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

def create_router(llm: ChatOpenAI):
    """
    Creates the intelligent routing system
    
    The router analyzes user input and determines which agent should handle the request:
    - WebScrape: For URL and web content requests
    - Knowledge: For queries about stored information
    - Conversation: For general chat and other interactions
    
    Args:
        llm: Language model instance
    
    Returns:
        function: Router function that classifies user intent
    """
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

def conversation_node(state, llm: ChatOpenAI):
    """
    Handles general conversation in the workflow
    
    Processes:
    1. Natural language understanding
    2. Response generation
    3. Conversation flow maintenance
    
    Args:
        state: Current conversation state
        llm: Language model instance
        
    Returns:
        dict: Updated state with conversation response
    """
    log_step('chat', "Processing conversation")
    try:
        messages = state["messages"]
        response = llm.invoke(messages)
        log_step('success', "Generated response")
        return {"messages": [response]}
    except Exception as e:
        log_step('error', f"Conversation error: {str(e)}")
        return {"messages": [HumanMessage(content="I'm having trouble processing that. Could you rephrase?")]}

def create_chat_workflow(llm: ChatOpenAI, scraping_tools: list, knowledge_tools: list):
    """
    Creates and configures the main chat workflow
    
    This function:
    1. Sets up the workflow graph
    2. Adds processing nodes
    3. Configures routing logic
    4. Establishes node connections
    
    Args:
        llm: Language model instance
        scraping_tools: List of web scraping tools
        knowledge_tools: List of knowledge base tools
    
    Returns:
        Workflow: Compiled workflow ready for execution
    """
    log_step('start', "Initializing chat workflow")
    
    # Create workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes with logging
    workflow.add_node("WebScrape", lambda state: webscrape_node(state, llm, scraping_tools))
    log_step('info', "Added WebScrape node")
    
    workflow.add_node("Knowledge", lambda state: knowledge_node(state, llm, knowledge_tools))
    log_step('info', "Added Knowledge node")
    
    workflow.add_node("Conversation", lambda state: conversation_node(state, llm))
    log_step('info', "Added Conversation node")
    
    workflow.add_node("router", create_router(llm))
    log_step('info', "Added Router node")

    # Add edges to connect nodes
    workflow.add_edge(START, "router")
    workflow.add_edge("WebScrape", END)
    workflow.add_edge("Knowledge", END)
    workflow.add_edge("Conversation", END)

    # Add conditional edges based on router decisions
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

def webscrape_node(state, llm: ChatOpenAI, scraping_tools: list):
    """
    Handles web scraping operations in the workflow
    
    Processes:
    1. URL extraction and validation
    2. Content scraping
    3. File saving
    4. Response formatting
    
    Args:
        state: Current conversation state
        llm: Language model instance
        scraping_tools: List of web scraping tools
        
    Returns:
        dict: Updated state with scraping results
    """
    log_step('web', "Processing web scraping request")
    try:
        agent = create_webscrape_agent(llm, scraping_tools)
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

def knowledge_node(state, llm: ChatOpenAI, knowledge_tools: list):
    """
    Handles knowledge base queries in the workflow
    
    Processes:
    1. Query understanding and classification
    2. Search method selection (vector/traditional/hybrid)
    3. Information retrieval and formatting
    
    Args:
        state: Current conversation state
        llm: Language model instance
        knowledge_tools: List of knowledge base tools
        
    Returns:
        dict: Updated state with knowledge base results
    """
    log_step('info', "Processing knowledge base query")
    try:
        # Determine search type based on query analysis
        query_analysis = llm.invoke([
            SystemMessage(content="""Analyze the query to determine the best search method:
            - Return "vector" for general, conceptual, or exploratory questions
            - Return "traditional" for specific topic or article requests
            - Return "hybrid" for complex queries needing both approaches
            
            Respond with only one word: vector, traditional, or hybrid"""),
            *state["messages"]
        ])
        
        search_type = query_analysis.content.strip().lower()
        log_step('info', f"Selected search type: {search_type}")
        
        # Get the actual query from the last user message
        query = state["messages"][-1].content
        
        # Create search command with type
        search_command = f"{query}|{search_type}"
        
        # Execute search through agent
        agent = create_knowledge_agent(llm, knowledge_tools)
        result = agent.invoke({
            "messages": [
                SystemMessage(content=f"Use the {search_type} search method to find information about: {query}"),
                *state["messages"]
            ]
        })
        
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