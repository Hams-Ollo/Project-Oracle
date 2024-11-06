from typing import Dict, Any
import openai

class BaseAgent:
    def __init__(self, model: str = "gpt-4", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.conversation_history = []
        
    async def process(self, message: str) -> str:
        """Base processing method to be implemented by specific agents"""
        raise NotImplementedError
        
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
        
    async def get_completion(self, messages: list) -> str:
        """Get completion from OpenAI API"""
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message.content 