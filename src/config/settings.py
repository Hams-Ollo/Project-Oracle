"""
Configuration and environment settings for the application.
"""

# Standard library imports
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate and load API keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

# Emoji constants for visual feedback
EMOJIS = {
    'start': '🚀',  # Process initiation
    'chat': '💭',   # Chat messages
    'web': '🌐',    # Web operations
    'route': '🔄',  # Routing decisions
    'error': '❌',  # Error states
    'success': '✅', # Successful operations
    'info': 'ℹ️ ',   # Information messages
    'think': '🤔',  # Processing states
    'done': '🏁',   # Completion
    'warn': '⚠️ '    # Warning messages
}

def log_step(emoji: str, message: str):
    """
    Provides consistent logging with emoji indicators for better visibility
    
    Args:
        emoji (str): Key for emoji from EMOJIS dict
        message (str): Message to be logged
    """
    print(f"\n{EMOJIS.get(emoji, 'ℹ️ ')} {message}")

def setup_scrape_directory():
    """
    Creates or verifies the scrape_dump directory for storing scraped content.
    Creates directory if it doesn't exist.
    
    Returns:
        Path: Path object pointing to scrape_dump directory
    """
    scrape_dir = Path("scrape_dump")
    if scrape_dir.exists():
        log_step('info', "Using existing scrape_dump directory")
    else:
        scrape_dir.mkdir()
        log_step('info', "Created scrape_dump directory")
    return scrape_dir