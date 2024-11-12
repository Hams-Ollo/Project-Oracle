from typing import Any, Dict, List
import asyncio
from .search_agent import SearchAgent
from .research_agent import ResearchAgent
from .onboarding_agent import OnboardingAgent
import openai

class Orchestrator:
    def __init__(self):
        self.agents = {
            "search": SearchAgent(),
            "research": ResearchAgent(),
            "onboarding": OnboardingAgent()
        }
        
    async def route_message(self, message: str) -> Dict[str, str]:
        """Route message to appropriate agent(s) and collect responses"""
        # Determine which agent(s) should handle the message
        routing_prompt = f"Classify this query for routing to agents (search, research, onboarding): {message}"
        routing_response = await self.get_routing_decision(routing_prompt)
        
        tasks = []
        for agent_name in routing_response:
            if agent_name in self.agents:
                tasks.append(self.process_with_agent(agent_name, self.agents[agent_name], message))
            
        responses = await asyncio.gather(*tasks)
        return {name: response for name, response in responses}
    
    async def get_routing_decision(self, prompt: str) -> List[str]:
        """Determine which agents should handle the message"""
        # Implementation using OpenAI to decide routing
        response = await openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a routing specialist. Return a comma-separated list of relevant agents (search, research, onboarding) based on the query."},
                {"role": "user", "content": prompt}
            ]
        )
        return [agent.strip() for agent in response.choices[0].message.content.split(",")]
    
    async def process_with_agent(self, agent_name: str, agent: Any, message: str) -> tuple:
        """Process message with specific agent"""
        response = await agent.process(message)
        return (agent_name, response) 