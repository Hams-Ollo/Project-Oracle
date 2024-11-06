from ..base_agent import BaseAgent
from swarm import Swarm, Agent

class ResearchTeam:
    def __init__(self):
        self.data_analyst = Agent(
            name="Data Analyst",
            instructions="You specialize in analyzing data and creating detailed statistical analysis."
        )
        
        self.fact_checker = Agent(
            name="Fact Checker",
            instructions="You verify information and find primary sources."
        )
        
        self.research_writer = Agent(
            name="Research Writer",
            instructions="You synthesize findings into clear, well-documented reports."
        )

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(model="gpt-4", temperature=0.5)
        self.research_team = ResearchTeam()
        
    async def process(self, message: str) -> str:
        # Step 1: Data Analysis
        analysis_response = await self.research_team.data_analyst.run(
            messages=[{"role": "user", "content": f"Analyze the following query: {message}"}]
        )
        
        # Step 2: Fact Checking
        fact_check_response = await self.research_team.fact_checker.run(
            messages=[
                {"role": "user", "content": message},
                {"role": "assistant", "content": analysis_response.messages[-1]["content"]}
            ]
        )
        
        # Step 3: Research Synthesis
        final_response = await self.research_team.research_writer.run(
            messages=[
                {"role": "system", "content": "Synthesize the analysis and fact-checking into a comprehensive report"},
                {"role": "user", "content": f"Analysis: {analysis_response.messages[-1]['content']}\n\nFact Check: {fact_check_response.messages[-1]['content']}"}
            ]
        )
        
        return final_response.messages[-1]["content"] 