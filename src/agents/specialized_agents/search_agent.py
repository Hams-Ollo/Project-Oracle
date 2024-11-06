from ..base_agent import BaseAgent
from duckduckgo_search import ddg
from typing import List, Dict

class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(model="gpt-4", temperature=0.7)
        self.system_prompt = """You are a search specialist agent that combines web search results with your knowledge to provide comprehensive, up-to-date information. Always cite your sources."""
        
    async def web_search(self, query: str, num_results: int = 3) -> List[Dict]:
        """Perform web search using DuckDuckGo"""
        results = ddg(query, max_results=num_results)
        return results
        
    async def process(self, message: str) -> str:
        # Perform web search
        search_results = await self.web_search(message)
        
        # Construct prompt with search results
        prompt = f"""Based on the following search results and your knowledge, provide a comprehensive response:
        
Search Results:
{search_results}

User Query: {message}

Provide a detailed response with citations."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        return await self.get_completion(messages) 