"""
Knowledge base service for managing and querying information.
"""

import json
from langchain_core.tools import Tool
from src.config.settings import log_step

class KnowledgeBase:
    """
    Knowledge base management and querying system
    
    Handles loading, searching, and retrieving information from a JSON-based knowledge base
    """
    def __init__(self, json_path: str = "knowledge_base.json"):
        """
        Initialize knowledge base from JSON file
        
        Args:
            json_path (str): Path to knowledge base JSON file
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # Create topic aliases and keywords for better matching
            self._create_topic_mappings()
            log_step('success', f"Knowledge base loaded successfully with {len(self.data['topics'])} topics and {len(self.data['articles'])} articles")
            log_step('info', f"Available topics: {list(self.data['topics'].keys())}")
        except Exception as e:
            log_step('error', f"Failed to load knowledge base: {e}")
            self.data = {"topics": {}, "articles": {}}
            self.topic_aliases = {}
            self.article_aliases = {}

    def _create_topic_mappings(self):
        """
        Create mappings for flexible topic matching
        
        Builds dictionaries of aliases for topics and articles to improve search flexibility
        """
        self.topic_aliases = {}
        self.article_aliases = {}
        
        # Create topic aliases
        for topic_key in self.data["topics"]:
            # Add the original key
            self.topic_aliases[topic_key.lower()] = topic_key
            # Add without underscores
            self.topic_aliases[topic_key.lower().replace('_', ' ')] = topic_key
            # Add key concepts as aliases
            for concept in self.data["topics"][topic_key].get("key_concepts", []):
                self.topic_aliases[concept.lower()] = topic_key
            # Add important figures as context
            for figure in self.data["topics"][topic_key].get("important_figures", []):
                self.topic_aliases[figure.lower()] = topic_key

        # Create article aliases
        for article_key in self.data["articles"]:
            # Add the original key
            self.article_aliases[article_key.lower()] = article_key
            # Add without underscores
            self.article_aliases[article_key.lower().replace('_', ' ')] = article_key
            # Add title as alias
            title = self.data["articles"][article_key].get("title", "").lower()
            self.article_aliases[title] = article_key
            # Add key points as context
            for point in self.data["articles"][article_key].get("key_points", []):
                key_terms = ' '.join(point.split()[:3]).lower()  # First three words of each key point
                self.article_aliases[key_terms] = article_key

    def _find_best_topic_match(self, query: str) -> str:
        """
        Find the best matching topic for a query
        
        Args:
            query (str): Search query
            
        Returns:
            str: Best matching topic or None if no match found
        """
        query = query.lower()
        
        # Direct match
        if query in self.topic_aliases:
            return self.topic_aliases[query]
        
        # Partial matches
        matches = []
        for alias, topic in self.topic_aliases.items():
            if query in alias or alias in query:
                matches.append(topic)
        
        return matches[0] if matches else None

    def search_topic(self, topic: str) -> str:
        """
        Search for information about a specific topic with flexible matching
        
        Args:
            topic (str): Topic to search for
            
        Returns:
            str: Formatted topic information or error message
        """
        log_step('info', f"Searching for topic: {topic}")
        
        matched_topic = self._find_best_topic_match(topic)
        if matched_topic:
            content = self.data["topics"][matched_topic]
            log_step('success', f"Found topic: {matched_topic}")
            
            # Get related topics
            related_topics = []
            for other_topic in self.data["topics"]:
                if other_topic != matched_topic:
                    if any(concept in content.get("key_concepts", []) 
                          for concept in self.data["topics"][other_topic].get("key_concepts", [])):
                        related_topics.append(other_topic)

            return f"""Topic: {matched_topic}

Definition: {content.get('definition', 'No definition available')}

Key Concepts: {', '.join(content.get('key_concepts', []))}

Important Figures: {', '.join(content.get('important_figures', []))}

Cultural Significance: {content.get('cultural_significance', 'No information available')}

Related Topics: {', '.join(related_topics) if related_topics else 'None found'}

Related Articles: {self._find_related_articles(matched_topic)}"""
        
        log_step('warn', f"No information found for topic: {topic}")
        return f"No information found for topic: {topic}. Available topics: {', '.join(self.data['topics'].keys())}"

    def _find_related_articles(self, topic: str) -> str:
        """
        Find articles related to a topic
        
        Args:
            topic (str): Topic to find related articles for
            
        Returns:
            str: Comma-separated list of related article titles
        """
        related = []
        topic_lower = topic.lower()
        
        for article_key, article in self.data["articles"].items():
            content = article.get("content", "").lower()
            if topic_lower in content or any(kw in content for kw in self.data["topics"][topic].get("key_concepts", [])):
                related.append(article["title"])
        
        return ', '.join(related) if related else 'None found'

    def get_article(self, title: str) -> str:
        """
        Get a specific article with flexible matching
        
        Args:
            title (str): Article title to search for
            
        Returns:
            str: Formatted article content or error message
        """
        title = title.lower()
        
        # Direct match
        if title in self.article_aliases:
            article_key = self.article_aliases[title]
            article = self.data["articles"][article_key]
            log_step('success', f"Found article: {article['title']}")
            
            return f"""Article: {article.get('title', 'Untitled')}

Summary: {article.get('summary', 'No summary available')}

Key Points:
{chr(10).join('- ' + point for point in article.get('key_points', []))}

Content:
{article.get('content', 'No content available')}

Related Topics: {self._find_related_topics(article_key)}"""
        
        # Partial matches
        for alias, key in self.article_aliases.items():
            if title in alias or alias in title:
                article = self.data["articles"][key]
                log_step('success', f"Found similar article: {article['title']}")
                return self.get_article(key)
        
        log_step('warn', f"No article found with title: {title}")
        return f"No article found with title: {title}. Try one of these: {', '.join(article['title'] for article in self.data['articles'].values())}"

    def _find_related_topics(self, article_key: str) -> str:
        """
        Find topics related to an article
        
        Args:
            article_key (str): Article key to find related topics for
            
        Returns:
            str: Comma-separated list of related topic names
        """
        related = []
        article_content = self.data["articles"][article_key].get("content", "").lower()
        
        for topic_key, topic in self.data["topics"].items():
            if (topic_key.lower() in article_content or 
                any(concept.lower() in article_content for concept in topic.get("key_concepts", []))):
                related.append(topic_key)
        
        return ', '.join(related) if related else 'None found'

    def list_topics(self) -> str:
        """
        List all available topics with their definitions
        
        Returns:
            str: Formatted list of topics and brief definitions
        """
        if not self.data["topics"]:
            return "No topics available in the knowledge base."
        
        topic_list = []
        for topic, content in self.data["topics"].items():
            definition = content.get("definition", "No definition available")
            # Take first sentence of definition for brevity
            short_def = definition.split('. ')[0]
            topic_list.append(f"- {topic}: {short_def}")
        
        return "Available Topics:\n" + "\n".join(topic_list)

    def list_articles(self) -> str:
        """
        List all available articles with their summaries
        
        Returns:
            str: Formatted list of articles and summaries
        """
        if not self.data["articles"]:
            return "No articles available in the knowledge base."
        
        article_list = []
        for article_key, article in self.data["articles"].items():
            title = article.get("title", article_key)
            summary = article.get("summary", "No summary available")
            article_list.append(f"- {title}: {summary}")
        
        return "Available Articles:\n" + "\n".join(article_list)

def create_knowledge_tools(kb: KnowledgeBase) -> list[Tool]:
    """
    Creates the knowledge base tools for use in the agent
    
    Args:
        kb (KnowledgeBase): Initialized KnowledgeBase instance
        
    Returns:
        list[Tool]: List of knowledge base tools
    """
    return [
        Tool(
            name="search_topic",
            description="Search for information about a specific topic in the knowledge base",
            func=kb.search_topic
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