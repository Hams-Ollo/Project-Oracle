from .base_agent import BaseAgent
from swarm import Agent
import yaml

class OnboardingAgent(BaseAgent):
    def __init__(self):
        super().__init__(model="gpt-4", temperature=0.7)
        self.load_onboarding_content()
        
        self.skill_advisor = Agent(
            name="Skill Advisor",
            instructions="You assess skill gaps and create learning paths."
        )
        
        self.process_guide = Agent(
            name="Process Guide",
            instructions="You explain workflows and organizational processes."
        )
        
    def load_onboarding_content(self):
        """Load onboarding documentation and knowledge base"""
        with open("config/onboarding_content.yaml", "r") as f:
            self.onboarding_content = yaml.safe_load(f)
    
    async def process(self, message: str) -> str:
        # Determine if this is a skill-related or process-related query
        classification_prompt = f"Classify if this query is about skills or processes: {message}"
        classification = await self.get_completion([
            {"role": "user", "content": classification_prompt}
        ])
        
        if "skill" in classification.lower():
            response = await self.skill_advisor.run(
                messages=[
                    {"role": "system", "content": str(self.onboarding_content['skills'])},
                    {"role": "user", "content": message}
                ]
            )
        else:
            response = await self.process_guide.run(
                messages=[
                    {"role": "system", "content": str(self.onboarding_content['processes'])},
                    {"role": "user", "content": message}
                ]
            )
            
        return response.messages[-1]["content"] 