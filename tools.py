import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, file_path: str = "RnD/knowledge_base.json"):
        try:
            with open(file_path, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            # Attempt to find file relative to current directory
            alt_path = file_path.split('/')[-1]
            try:
                with open(alt_path, 'r') as f:
                    self.data = json.load(f)
            except FileNotFoundError as e:
                logger.error(f"Could not find knowledge base file: {e}")
                self.data = {"topics": {}, "articles": {}}
    
    def search_topic(self, topic: str) -> Dict:
        """Search for information about a specific topic"""
        return self.data.get("topics", {}).get(topic, {})
    
    def get_article(self, article_id: str) -> Dict:
        """Get a specific article"""
        return self.data.get("articles", {}).get(article_id, {})
    
    def list_topics(self) -> List[str]:
        """List all available topics"""
        return list(self.data.get("topics", {}).keys())

class ScheduleManager:
    def __init__(self, file_path: str = "RnD/schedule.csv"):
        self.file_path = file_path
        try:
            self.schedule = pd.read_csv(file_path)
        except FileNotFoundError:
            # Attempt to find file relative to current directory
            self.file_path = file_path.split('/')[-1]
            try:
                self.schedule = pd.read_csv(self.file_path)
            except FileNotFoundError:
                logger.warning("No schedule file found. Creating new schedule.")
                self.schedule = pd.DataFrame(columns=[
                    'date', 'time_block', 'event_type', 'description', 'status'
                ])
                self.schedule.to_csv(self.file_path, index=False)
    
    def get_schedule(self, date: Optional[str] = None) -> pd.DataFrame:
        """Get schedule for a specific date or all schedules"""
        if date:
            return self.schedule[self.schedule['date'] == date]
        return self.schedule
    
    def add_event(self, date: str, time_block: str, event_type: str, description: str):
        """Add a new event to the schedule"""
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        if not self.check_availability(date, time_block):
            raise ValueError("Time block is not available")
            
        new_event = pd.DataFrame({
            'date': [date],
            'time_block': [time_block],
            'event_type': [event_type],
            'description': [description],
            'status': ['scheduled']
        })
        self.schedule = pd.concat([self.schedule, new_event], ignore_index=True)
        self.schedule.to_csv(self.file_path, index=False)
        return f"Event added successfully for {date} at {time_block}"
    
    def check_availability(self, date: str, time_block: str) -> bool:
        """Check if a time block is available"""
        conflicts = self.schedule[
            (self.schedule['date'] == date) & 
            (self.schedule['time_block'] == time_block)
        ]
        return len(conflicts) == 0

class ContentGenerator:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
    
    def generate_article(self, topic: str, style: str = "general") -> Dict:
        """Generate an article based on topic and style"""
        topic_info = self.kb.search_topic(topic)
        if not topic_info:
            return {"error": "Topic not found"}
        
        # This would typically use an LLM to generate content
        # For now, we'll return a structured template
        return {
            "title": f"{style.title()} Guide to {topic.title()}",
            "content": f"Generated content about {topic} in {style} style",
            "sources": [topic_info],
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "style": style,
                "topic": topic
            }
        }