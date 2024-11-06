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

# IMPORTS
import os
from typing import Annotated, Sequence, Tuple, TypedDict, Any, List
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import MessageGraph, StateGraph
from langchain_openai import ChatOpenAI
import operator
from enum import Enum
import json
import openai
from datetime import datetime
import sys
import signal
from utils.doc_loader import DocumentationLoader

# Load environment variables and configure settings
load_dotenv()
print("[INFO] Environment variables loaded successfully")

# Configure OpenAI globally
openai.api_key = os.getenv("OPENAI_API_KEY")
print("[CONFIG] OpenAI API configured globally")

def format_debug_info(message, level="INFO"):
    """Format debug information with consistent styling and emojis"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {
        "INFO": "ℹ️ \033[94m[INFO]\033[0m",          # Blue with info emoji
        "DEBUG": "🔍 \033[92m[DEBUG]\033[0m",        # Green with magnifying glass
        "ERROR": "❌ \033[91m[ERROR]\033[0m",        # Red with cross
        "SYSTEM": "🤖 \033[95m[SYSTEM]\033[0m",      # Purple with robot
        "TRANSFER": "🔄 \033[93m[TRANSFER]\033[0m",  # Yellow with transfer
        "ASSISTANT": "🧠 \033[96m[AI]\033[0m",       # Cyan with brain
        "FLOW": "📊 \033[95m[FLOW]\033[0m",         # Purple with graph
        "STATE": "📝 \033[93m[STATE]\033[0m",        # Yellow with notepad
    }
    return f"[{timestamp}] {prefix.get(level, '[LOG]')} {message}"

# Define state types
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    next_agent: str | None
    context: dict
    debug: bool
    conversation_active: bool
    current_agent: str
    turn_count: int
    error: str | None
    doc_context: List[str]

# Define agent roles
class AgentRole(Enum):
    ONBOARDING = "onboarding"
    TECHNICAL = "technical"
    PROCESS = "process"

class AgentCapability(Enum):
    GENERAL = "general_support"
    TECHNICAL = "technical_support"
    PROCESS = "process_guidance"
    TRAINING = "training_support"

# Create agents with specific roles
def create_agent(role: AgentRole):
    """Create an agent with specific role and instructions"""
    doc_loader = DocumentationLoader()
    
    instructions = {
        AgentRole.ONBOARDING: """You are an onboarding specialist helping new team members understand their role and required skills.
        Use the provided documentation context to guide your responses.
        Pay special attention to:
        1. Initial assessment of team member's background
        2. Required skills and knowledge gaps
        3. Training recommendations
        4. Team integration guidance
        
        When documentation context is provided, incorporate it into your responses while maintaining natural conversation.""",
        
        AgentRole.TECHNICAL: """You are a technical advisor providing detailed technical guidance and best practices.
        Focus on:
        1. Technical implementation details
        2. Best practices and standards
        3. Problem-solving approaches
        4. Technology stack recommendations""",
        
        AgentRole.PROCESS: """You are a process guide explaining workflows and organizational procedures.
        Emphasize:
        1. Standard operating procedures
        2. Workflow optimization
        3. Compliance requirements
        4. Process improvement suggestions"""
    }
    
    print(format_debug_info(f"Creating {role.value} agent", "INFO"))
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=2000,
        request_timeout=30
    )
    
    def agent_function(state: AgentState) -> AgentState:
        """Process messages and determine if handoff is needed"""
        if state["debug"]:
            print(format_debug_info(f"Agent {role.value} processing message", "FLOW"))
        
        # Get relevant documentation based on the last message
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            # Get relevant docs based on agent role
            relevant_docs = doc_loader.get_relevant_docs(
                last_message.content,
                context_type=role.name  # This will match with DocCategory
            )
            
            # Format documentation context
            doc_context = []
            for doc in relevant_docs:
                doc_context.append(f"\n### {doc['doc_name']} ({doc['category']})")
                for section_name, content in doc['sections'].items():
                    doc_context.append(f"\n#### {section_name}\n{content}")
            
            state["doc_context"] = doc_context
        
        # Create a combined system message with documentation context
        system_content = instructions[role]
        if state.get("doc_context"):
            system_content += "\n\nRelevant documentation context:\n"
            for doc in state["doc_context"]:
                system_content += f"\n---\n{doc}\n---\n"
        
        system_message = SystemMessage(content=system_content)
        
        if state.get("turn_count", 0) > 5:
            if state["debug"]:
                print(format_debug_info(f"🔄 Maximum turns ({state['turn_count']}) reached for {role.value}", "FLOW"))
            state["next_agent"] = "technical" if role == AgentRole.ONBOARDING else "onboarding"
            return state
        
        if state["debug"]:
            print(format_debug_info(f"Turn count: {state.get('turn_count', 0)}", "STATE"))
        
        current_messages = list(state["messages"])
        
        try:
            # Prepare messages for the LLM
            messages_for_llm = [system_message] + current_messages
            response = llm.invoke(messages_for_llm)
            
            # Update state with response
            new_messages = current_messages + [response]
            state["messages"] = new_messages
            
            # Check for handoff in response
            try:
                parsed = json.loads(response.content)
                if "handoff" in parsed:
                    if state["debug"]:
                        print(format_debug_info(f"Handoff requested to {parsed['handoff']}", "TRANSFER"))
                    state["next_agent"] = parsed["handoff"]
            except json.JSONDecodeError:
                state["next_agent"] = None
            
            # Update turn count
            state["turn_count"] = state.get("turn_count", 0) + 1
            
            return state
            
        except Exception as e:
            if state["debug"]:
                print(format_debug_info(f"Error in agent function: {str(e)}", "ERROR"))
            state["error"] = str(e)
            return state
    
    return agent_function

def should_continue(state: AgentState) -> bool:
    """Determine if the conversation should continue"""
    if state.get("turn_count", 0) >= 3:
        if state["debug"]:
            print(format_debug_info("🔄 Forcing handoff due to max consecutive turns", "FLOW"))
        return False
    
    if not state["conversation_active"]:
        if state["debug"]:
            print(format_debug_info("Conversation marked as complete", "SYSTEM"))
        return False
    
    if not state["messages"]:
        if state["debug"]:
            print(format_debug_info("No messages in state", "DEBUG"))
        return False
    
    if state.get("error"):
        if state["debug"]:
            print(format_debug_info(f"Error detected: {state['error']}", "ERROR"))
        return False
    
    if state.get("turn_count", 0) >= state["context"].get("max_turns", 50):
        if state["debug"]:
            print(format_debug_info("Maximum turns reached", "SYSTEM"))
        return False
    
    last_message = state["messages"][-1]
    termination_phrases = [
        "goodbye", "bye", "quit", "exit", "end",
        "thank you, that's all", "that's all for now"
    ]
    
    if isinstance(last_message, HumanMessage):
        content = last_message.content.lower()
        if any(phrase in content for phrase in termination_phrases):
            if state["debug"]:
                print(format_debug_info("Termination phrase detected", "SYSTEM"))
            return False
    
    if state["debug"] and state["conversation_active"]:
        print(format_debug_info(f"Current turn: {state.get('turn_count', 0)}/{state['context'].get('max_turns', 50)}", "STATE"))
    
    return True

def should_route(state: AgentState) -> bool:
    """Determine if we should route to a different agent"""
    if not state["messages"]:
        return False
    
    last_message = state["messages"][-1]
    try:
        if isinstance(last_message, AIMessage):
            parsed = json.loads(last_message.content)
            return "handoff" in parsed
    except (json.JSONDecodeError, AttributeError):
        return False
    
    return False

def route_message(state: AgentState) -> str:
    """Route to the appropriate agent based on the last message"""
    last_message = state["messages"][-1]
    try:
        if isinstance(last_message, AIMessage):
            parsed = json.loads(last_message.content)
            next_agent = parsed.get("handoff", "onboarding")
            if state["debug"]:
                print(format_debug_info(f"Routing to {next_agent}", "TRANSFER"))
            return next_agent
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return "onboarding"

def create_agent_graph():
    """Create and configure the agent workflow graph"""
    print(format_debug_info("Initializing agent graph", "SYSTEM"))
    
    # Initialize agents
    agents = {
        "onboarding": create_agent(AgentRole.ONBOARDING),
        "technical": create_agent(AgentRole.TECHNICAL),
        "process": create_agent(AgentRole.PROCESS)
    }
    
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    for agent_name, agent_func in agents.items():
        workflow.add_node(agent_name, agent_func)
    
    # Add conditional edges
    for agent_name in agents:
        # First check if we should continue
        workflow.add_conditional_edges(
            agent_name,
            should_continue,
            {
                True: agent_name + "_router",  # Route to a router node
                False: "end"
            }
        )
        
        # Add a router node for this agent
        workflow.add_node(
            agent_name + "_router",
            lambda state: {
                **state, 
                "next_agent": route_message(state),
                "_previous_agent": state.get("current_agent")  # Track previous agent
            }
        )
        
        # Add edges from router to all possible agents
        workflow.add_conditional_edges(
            agent_name + "_router",
            lambda state: state["next_agent"],
            {
                "onboarding": "onboarding",
                "technical": "technical",
                "process": "process",
            }
        )
    
    # Add end node
    def end_conversation(state: AgentState) -> AgentState:
        """Handle conversation end gracefully"""
        if state["debug"]:
            print(format_debug_info("Ending conversation", "SYSTEM"))
        state["conversation_active"] = False
        return state
    
    workflow.add_node("end", end_conversation)
    
    # Set entry point
    workflow.set_entry_point("onboarding")
    
    return workflow.compile()

def format_response(response_content: str) -> str:
    """Format the response for display"""
    try:
        # Try to parse as JSON to remove handoff instructions
        parsed = json.loads(response_content)
        if "handoff" in parsed:
            # Extract just the message part if it exists
            return parsed.get("message", response_content)
    except json.JSONDecodeError:
        pass
    return response_content

def main():
    """Main function to run the agent system"""
    print(format_debug_info("🚀 Launching Team Assistant", "SYSTEM"))
    print(format_debug_info("💡 Type 'quit' to exit or press Ctrl+C", "SYSTEM"))
    print(format_debug_info("📚 Loading documentation...", "SYSTEM"))
    
    # Initialize documentation loader
    doc_loader = DocumentationLoader()
    initial_docs = doc_loader.get_all_docs()
    print(format_debug_info(f"Loaded {len(initial_docs)} documentation files", "SYSTEM"))
    
    graph = create_agent_graph()
    context = {
        "user_name": "New Team Member",
        "debug": True,
        "max_turns": 50,
        "start_time": datetime.now().isoformat(),
        "available_docs": list(initial_docs.keys())
    }
    
    try:
        while True:
            try:
                user_input = input("\033[1m💬 You:\033[0m ")
                
                if user_input.lower() in ['quit', 'exit']:
                    raise KeyboardInterrupt
                
                # Initialize state with user input
                state = AgentState(
                    messages=[HumanMessage(content=user_input)],
                    next_agent=None,
                    context=context,
                    debug=True,
                    conversation_active=True,
                    current_agent="onboarding",
                    turn_count=0,
                    error=None,
                    doc_context=[]
                )
                
                # Process through graph with timeout
                print(format_debug_info("Processing response...", "DEBUG"))
                result = graph.invoke(state)
                
                # Add state transition debugging
                if isinstance(result, dict):
                    print(format_debug_info(
                        f"Agent: {result.get('current_agent', 'unknown')} → "
                        f"Next: {result.get('next_agent', 'same')}",
                        "FLOW"
                    ))
                
                # Handle response
                if isinstance(result, dict) and "messages" in result:
                    last_message = result["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        response_content = format_response(last_message.content)
                        print(f"\n\033[1m🤖 Assistant:\033[0m \033[96m{response_content}\033[0m")
                
                print("\n" + "-"*80 + "\n")
                
            except Exception as e:
                print(format_debug_info(f"⚠️ Error: {e}", "ERROR"))
                print(format_debug_info("🔄 Please try again or type 'quit' to exit.", "SYSTEM"))
                
    except KeyboardInterrupt:
        print("\n")
        print(format_debug_info("👋 Gracefully shutting down...", "SYSTEM"))
        print(format_debug_info("✨ Thanks for using the Team Assistant!", "SYSTEM"))
        sys.exit(0)

if __name__ == "__main__":
    main()