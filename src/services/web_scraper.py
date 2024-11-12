"""
Web scraping service and related utilities.
"""

from datetime import datetime
import re
from pathlib import Path
from langchain_core.tools import Tool
from langchain_community.document_loaders.firecrawl import FireCrawlLoader

from src.config.settings import log_step, setup_scrape_directory

class WebScraper:
    """
    Web scraping tool using FireCrawl API
    
    Handles web content scraping and saving to markdown files
    """
    def __init__(self, api_key: str):
        """
        Initialize scraper with API key and setup directory
        
        Args:
            api_key (str): FireCrawl API key for authentication
        """
        self.api_key = api_key
        self.scrape_dir = setup_scrape_directory()

    def save_markdown(self, content: str, url: str) -> str:
        """
        Save markdown content to file and return the filepath
        
        Args:
            content (str): Content to save
            url (str): Source URL for reference
            
        Returns:
            str: Path to saved file or empty string if save fails
        """
        filename = sanitize_filename(url)
        filepath = self.scrape_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Content from {url}\n\n")
                f.write(content)
            log_step('success', f"Saved content to {filepath}")
            return str(filepath)
        except Exception as e:
            log_step('error', f"Failed to save content: {e}")
            return ""

    def scrape_url(self, url: str) -> str:
        """
        Scrape a single webpage and save its content
        
        Args:
            url (str): URL to scrape
            
        Returns:
            str: Status message with results or error
        """
        try:
            log_step('web', f"Attempting to scrape URL: {url}")
            loader = FireCrawlLoader(
                api_key=self.api_key,
                url=url,
                mode="scrape"
            )
            log_step('think', "Loading content...")
            docs = loader.load()
            if not docs:
                log_step('warn', "No content found")
                return "No content found for this URL."
            
            log_step('success', "Content retrieved successfully")
            
            # Save the content and get the filepath
            content = docs[0].page_content
            filepath = self.save_markdown(content, url)
            
            if filepath:
                return f"""Successfully scraped and saved content!
                
                Content has been saved to: {filepath}
                
                Here's a brief summary of what I found:
                {content[:500]}...
                
                You can find the complete content in the saved file."""
            else:
                return f"Successfully scraped but failed to save content. Here's what I found:\n\n{content[:1000]}..."
            
        except Exception as e:
            log_step('error', f"Scraping failed: {str(e)}")
            return f"Failed to scrape URL: {str(e)}"

def sanitize_filename(url: str) -> str:
    """
    Converts a URL into a safe filename with timestamp to prevent conflicts
    
    Args:
        url (str): URL to be converted
        
    Returns:
        str: Sanitized filename with timestamp appended
    """
    # Remove protocol and special characters
    filename = re.sub(r'https?://', '', url)
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{filename}_{timestamp}.md"

def create_scraping_tools(scraper: WebScraper) -> list[Tool]:
    """
    Creates the web scraping tools for use in the agent
    
    Args:
        scraper (WebScraper): Initialized WebScraper instance
        
    Returns:
        list[Tool]: List of scraping tools
    """
    return [
        Tool(
            name="scrape_webpage",
            description="Scrape content from a webpage. Input should be a valid URL.",
            func=scraper.scrape_url
        )
    ]