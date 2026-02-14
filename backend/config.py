"""
Configuration settings for the Play Store Scraper API
"""

from enum import Enum
from typing import Dict

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Scraper Configuration
SCRAPER_CONFIG = {
    "country": "us",
    "lang": "en",
    "count": 50,
    "sort": "NEWEST"  # Options: NEWEST, RATING, HELPFUL
}

# API Configuration
API_TITLE = "US Play Store Scraper API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Professional API to scrape apps and games from the US Google Play Store"

# Logging Configuration
LOG_LEVEL = "INFO"

# Error Messages
ERROR_MESSAGES = {
    "category_not_found": "Category '{category}' not found",
    "scrape_failed": "Failed to scrape category '{category}'",
    "invalid_input": "Invalid input provided",
}

# Category List (49 total: 34 apps + 15 games)
CATEGORIES = {
    # App Categories (34)
    "apps": {
        "art_design": "ART_AND_DESIGN",
        "auto": "AUTO_AND_VEHICLES",
        "beauty": "BEAUTY",
        "books": "BOOKS_AND_REFERENCE",
        "business": "BUSINESS",
        "comics": "COMICS",
        "communication": "COMMUNICATION",
        "education": "EDUCATION",
        "entertainment": "ENTERTAINMENT",
        "events": "EVENTS",
        "finance": "FINANCE",
        "food": "FOOD_AND_DRINK",
        "health": "HEALTH_AND_FITNESS",
        "house": "HOUSE_AND_HOME",
        "libraries": "LIBRARIES_AND_DEMO",
        "lifestyle": "LIFESTYLE",
        "maps": "MAPS_AND_NAVIGATION",
        "medical": "MEDICAL",
        "music": "MUSIC_AND_AUDIO",
        "news": "NEWS_AND_MAGAZINES",
        "parenting": "PARENTING",
        "personalization": "PERSONALIZATION",
        "photography": "PHOTOGRAPHY",
        "productivity": "PRODUCTIVITY",
        "shopping": "SHOPPING",
        "social": "SOCIAL",
        "sports": "SPORTS",
        "tools": "TOOLS",
        "travel": "TRAVEL_AND_LOCAL",
        "video": "VIDEO_PLAYERS",
        "weather": "WEATHER",
        "work": "WORK_PROFILE",
    },
    
    # Game Categories (15)
    "games": {
        "action": "GAME_ACTION",
        "adventure": "GAME_ADVENTURE",
        "arcade": "GAME_ARCADE",
        "board": "GAME_BOARD",
        "card": "GAME_CARD",
        "casual": "GAME_CASUAL",
        "educational_game": "GAME_EDUCATIONAL",
        "music_game": "GAME_MUSIC",
        "puzzle": "GAME_PUZZLE",
        "racing": "GAME_RACING",
        "role_playing": "GAME_ROLE_PLAYING",
        "simulation": "GAME_SIMULATION",
        "sports_game": "GAME_SPORTS",
        "strategy": "GAME_STRATEGY",
        "trivia": "GAME_TRIVIA",
    }
}


def get_all_categories() -> Dict[str, str]:
    """Get all categories as a single dictionary"""
    all_categories = {}
    all_categories.update(CATEGORIES["apps"])
    all_categories.update(CATEGORIES["games"])
    return all_categories


def get_app_categories() -> Dict[str, str]:
    """Get only app categories"""
    return CATEGORIES["apps"].copy()


def get_game_categories() -> Dict[str, str]:
    """Get only game categories"""
    return CATEGORIES["games"].copy()


if __name__ == "__main__":
    # Print category summary
    all_cats = get_all_categories()
    print(f"Total Categories: {len(all_cats)}")
    print(f"App Categories: {len(CATEGORIES['apps'])}")
    print(f"Game Categories: {len(CATEGORIES['games'])}")
