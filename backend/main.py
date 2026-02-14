from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from google_play_scraper import search
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Category queries: normalized category -> descriptive search phrase
APP_CATEGORY_QUERIES = {
    "art_design": "art and design drawing apps",
    "auto": "car maintenance and auto care apps",
    "beauty": "beauty tutorials and makeup apps",
    "books": "ebook reader and book apps",
    "business": "small business productivity apps",
    "comics": "digital comics reader apps",
    "communication": "messaging and calling apps",
    "education": "education learning apps",
    "entertainment": "entertainment streaming apps",
    "events": "event tickets and planner apps",
    "finance": "personal finance budgeting apps",
    "food": "food delivery and recipe apps",
    "health": "health and fitness workout apps",
    "house": "home design and real estate apps",
    "libraries": "demo and libraries developer apps",
    "lifestyle": "lifestyle inspiration apps",
    "maps": "maps and navigation gps apps",
    "medical": "medical reference apps",
    "music": "music streaming apps",
    "news": "news and magazines apps",
    "parenting": "parenting baby tracker apps",
    "personalization": "android launcher personalization apps",
    "photography": "photo editor camera apps",
    "productivity": "productivity task manager apps",
    "shopping": "shopping deals apps",
    "social": "social media community apps",
    "sports": "sports scores apps",
    "tools": "android utility tools apps",
    "travel": "travel planning and booking apps",
    "video": "video streaming and player apps",
    "weather": "weather forecast apps",
    "work": "work profile enterprise apps",
}

GAME_CATEGORY_QUERIES = {
    "action": "action games android",
    "adventure": "adventure games android",
    "arcade": "arcade games android",
    "board": "board games android",
    "card": "card games android",
    "casual": "casual games android",
    "educational_game": "educational games for kids",
    "music_game": "music rhythm games android",
    "puzzle": "puzzle games android",
    "racing": "racing games android",
    "role_playing": "role playing rpg games android",
    "simulation": "simulation games android",
    "sports_game": "sports games android",
    "strategy": "strategy games android",
    "trivia": "trivia quiz games android",
}

CATEGORY_QUERIES = {**APP_CATEGORY_QUERIES, **GAME_CATEGORY_QUERIES}

PER_KEYWORD_HITS = 200


def _build_category_keywords() -> Dict[str, List[str]]:
    """Generate multiple keyword variations per category for broader coverage."""
    keywords: Dict[str, List[str]] = {}
    for category, base_phrase in CATEGORY_QUERIES.items():
        readable = category.replace("_", " ")
        variants = [
            base_phrase,
            f"{readable} apps",
            f"best {readable} apps",
            f"popular {readable} apps",
            f"top {readable} android apps",
            f"{readable} app download",
        ]
        # Remove duplicates while preserving order
        unique_variants = list(dict.fromkeys(variant for variant in variants if variant))
        keywords[category] = unique_variants
    return keywords


CATEGORY_KEYWORDS = _build_category_keywords()


def _parse_int(value: Optional[object]) -> Optional[int]:
    """Parse various Play Store numeric strings (e.g., '10,000+', '1.5M') into ints."""
    if value is None:
        return None
    if isinstance(value, bool):  # guard against bool subclass of int
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        normalized = value.strip().lower().replace(",", "")
        multiplier = 1
        if normalized.endswith("+"):
            normalized = normalized[:-1]
        if normalized.endswith("m"):
            multiplier = 1_000_000
            normalized = normalized[:-1]
        elif normalized.endswith("k"):
            multiplier = 1_000
            normalized = normalized[:-1]
        normalized = normalized.strip()
        if not normalized:
            return None
        try:
            return int(float(normalized) * multiplier)
        except ValueError:
            return None
    return None


def _gather_category_results(category: str) -> Tuple[List[dict], List[dict]]:
    """Run multi-keyword searches for a category and return raw plus deduped entries."""
    keywords = CATEGORY_KEYWORDS.get(category, [])
    raw_results: List[dict] = []
    deduped: Dict[str, dict] = {}

    for keyword in keywords:
        try:
            logger.info("[SCRAPE] category=%s keyword='%s'", category, keyword)
            search_results = search(
                query=keyword,
                n_hits=PER_KEYWORD_HITS,
                lang="en",
                country="us"
            )
        except Exception as exc:
            logger.warning("[SCRAPE_ERROR] keyword='%s' error=%s", keyword, exc)
            continue

        if isinstance(search_results, dict) and "apps" in search_results:
            apps_batch = search_results.get("apps", [])
        elif isinstance(search_results, list):
            apps_batch = search_results
        else:
            apps_batch = []

        raw_results.extend(apps_batch)
        for app_data in apps_batch:
            app_id = app_data.get("appId")
            if not app_id or app_id in deduped:
                continue
            deduped[app_id] = app_data

    return raw_results, list(deduped.values())


def _to_app_info(app_data: dict) -> Optional[AppInfo]:
    """Convert raw scraper payload into AppInfo if possible."""
    app_url = app_data.get('url')
    if not app_url:
        app_id_for_url = app_data.get('appId')
        if not app_id_for_url:
            return None
        app_url = f"https://play.google.com/store/apps/details?id={app_id_for_url}"

    return AppInfo(
        name=app_data.get('title', 'N/A'),
        rating=app_data.get('score'),
        reviews=_parse_int(app_data.get('reviews')),
        min_installs=_parse_int(app_data.get('installs')),
        url=app_url
    )

# Initialize FastAPI app
app_instance = FastAPI(
    title="US Play Store Scraper API",
    description="Professional API to scrape apps and games from the US Google Play Store",
    version="1.0.0",
)


# Pydantic model for cleaned app response
class AppInfo(BaseModel):
    """Minimal app payload returned to clients"""
    name: str = Field(..., description="App title")
    rating: Optional[float] = Field(None, description="App rating (0-5)")
    reviews: Optional[int] = Field(None, description="Total number of reviews")
    min_installs: Optional[int] = Field(None, alias="minInstalls", description="Minimum installs count")
    url: str = Field(..., description="Direct Google Play URL")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True


class ScrapeResponse(BaseModel):
    """Response model for scrape endpoint"""
    category: str = Field(..., description="Requested category")
    total_raw_collected: int = Field(..., description="Total apps collected across all keywords")
    total_unique_after_dedup: int = Field(..., description="Unique apps after deduplication")
    total_returned: int = Field(..., description="Apps returned after optional filtering and limiting")
    apps: List[AppInfo] = Field(..., description="List of returned apps")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    suggested_categories: List[str] = Field(default_factory=list, description="List of suggested categories")


class DeepScanAppInfo(BaseModel):
    """Low-rated app info for deep scan"""
    title: str = Field(..., description="App title")
    app_id: str = Field(..., alias="appId", description="Unique app identifier")
    score: float = Field(..., description="App rating (0-5)")
    developer: str = Field(..., description="Developer name")
    description: Optional[str] = Field(None, description="App description")
    installs: Optional[str] = Field(None, description="Number of installs")

    class Config:
        populate_by_name = True


class DeepScanResponse(BaseModel):
    """Response model for deep scan endpoint"""
    keyword_searched: str = Field(..., description="Keyword that was searched")
    total_apps_scanned: int = Field(..., description="Total apps scanned")
    low_rated_apps_count: int = Field(..., description="Number of low-rated apps found")
    apps: List[DeepScanAppInfo] = Field(..., description="List of low-rated apps")


@app_instance.get("/", tags=["Root"])
async def root():
    """
    Welcome endpoint with instructions
    """
    return {
        "message": "Welcome to US Play Store Scraper API",
        "description": "Scrape apps and games from the Google Play Store",
        "endpoints": {
            "documentation": "/docs",
            "scrape": "/scrape/{category_name}",
            "health_check": "/health"
        },
        "instructions": "Visit /docs for interactive documentation and a complete list of all available categories",
        "example_usage": "/scrape/action (for action games) or /scrape/productivity (for productivity apps)"
    }


@app_instance.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "US Play Store Scraper API"}


@app_instance.get(
    "/scrape/{category_name}",
    response_model=ScrapeResponse,
    tags=["Scraping"],
    responses={
        200: {"description": "Successfully scraped apps"},
        400: {"description": "Invalid category", "model": ErrorResponse}
    }
)
async def scrape_category(
    category_name: str,
    limit: int = Query(200, ge=1, le=1000, description="Maximum apps to return after dedup and filtering"),
    underperforming_only: bool = Query(
        False,
        description="If true, only include apps with rating < 4.0"
    )
):
    """
    Scrape apps/games from the US store using keyword search queries.
    
    **Features:**
    - Always queries the US Play Store (`country='us'`, `lang='en'`)
    - Executes multiple search queries per category and merges the results
    - Each keyword search uses `n_hits=200`, `lang='en'`, `country='us'`
    - Deduplicates apps via `appId` before optional filtering
    - Optional filter `underperforming_only=true` keeps apps with rating < 4.0
    - Returns clean metadata (name, rating, reviews, min_installs, url)
    
    **Parameters:**
    - **category_name**: Category key defined in `CATEGORY_QUERIES`
    
    **Returns:**
    - Transparent counts for raw collected, deduped, and returned apps
    - Optional filtering for underperforming apps (rating < 4.0)
    - Limit applied after deduplication and filtering
    """
    
    # Normalize category name: lowercase and replace spaces with underscores
    normalized_category = category_name.lower().replace(" ", "_")
    
    # Check if category exists in mapping
    if normalized_category not in CATEGORY_QUERIES:
        # Get suggested categories (similar matches)
        suggestions = [cat for cat in CATEGORY_QUERIES.keys() 
                      if normalized_category[:3] in cat or cat.startswith(normalized_category[:2])][:5]
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Category '{category_name}' not found",
                "suggested_categories": suggestions if suggestions else list(CATEGORY_QUERIES.keys())[:10],
                "available_categories_count": len(CATEGORY_QUERIES),
                "visit_docs": "Check /docs for the complete list of categories"
            }
        )
    
    try:
        raw_results, unique_results = _gather_category_results(normalized_category)
        total_raw_collected = len(raw_results)
        total_unique_after_dedup = len(unique_results)

        if underperforming_only:
            candidate_results = [
                app for app in unique_results
                if app.get('score') is not None and app.get('score') < 4.0
            ]
        else:
            candidate_results = unique_results

        apps_payload: List[AppInfo] = []
        for app_data in candidate_results:
            app_info = _to_app_info(app_data)
            if not app_info:
                continue
            apps_payload.append(app_info)
            if len(apps_payload) >= limit:
                break

        logger.info(
            "[SCRAPE_DONE] category=%s raw=%s unique=%s returned=%s",
            normalized_category,
            total_raw_collected,
            total_unique_after_dedup,
            len(apps_payload)
        )

        return ScrapeResponse(
            category=normalized_category,
            total_raw_collected=total_raw_collected,
            total_unique_after_dedup=total_unique_after_dedup,
            total_returned=len(apps_payload),
            apps=apps_payload
        )
    
    except Exception as e:
        logger.error(f"Error scraping category {normalized_category}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to scrape category",
                "details": str(e),
                "category": normalized_category
            }
        )


@app_instance.get("/categories", tags=["Information"])
async def list_categories():
    """
    Get all available categories
    """
    app_categories = sorted(APP_CATEGORY_QUERIES.keys())
    game_categories = sorted(GAME_CATEGORY_QUERIES.keys())
    
    return {
        "total_categories": len(CATEGORY_QUERIES),
        "app_categories": {
            "count": len(app_categories),
            "categories": app_categories
        },
        "game_categories": {
            "count": len(game_categories),
            "categories": game_categories
        },
        "usage": "Use these category names in /scrape/{category_name} endpoint"
    }


@app_instance.get(
    "/deep-scan/{keyword}",
    response_model=DeepScanResponse,
    tags=["Deep Scan"],
    responses={
        200: {"description": "Successfully scanned and found low-rated apps"},
        404: {"description": "No results found for keyword"}
    }
)
async def deep_scan(keyword: str):
    """
    Deep scan for low-rated apps using keyword search
    
    **Features:**
    - Scans 500 apps from US Google Play Store (us, en locked)
    - Filters to show apps with rating between 3.0 and 4.0
    - Excludes new apps with no ratings (score = 0)
    - Sorts by worst rating first (ascending score)
    
    **Parameters:**
    - **keyword**: Search keyword (e.g., 'vpn', 'antivirus', 'weather')
    
    **Returns:**
    - Total apps scanned
    - Count of low-rated apps found
    - List of apps with Title, AppId, Score, Developer, Description, Installs
    
    **Example:**
    - `/deep-scan/vpn` - Find apps with rating 3.0-4.0
    - `/deep-scan/antivirus` - Search antivirus apps
    """
    
    if not keyword or len(keyword.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail={"error": "Keyword cannot be empty"}
        )
    
    keyword = keyword.strip()
    logger.info(f"[DEEP_SCAN] Searching for keyword: '{keyword}'")
    logger.info(f"[SEARCH_PARAMS] country='us', lang='en', n_hits=500")
    
    try:
        # Scan with 500 hits for comprehensive deep analysis
        results = search(
            query=keyword,
            n_hits=500,
            lang='en',
            country='us'
        )
        
        # Handle different response formats
        if isinstance(results, dict) and 'apps' in results:
            apps_list = results.get('apps', [])
        elif isinstance(results, list):
            apps_list = results
        else:
            apps_list = []
        
        if not apps_list:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"No results found for keyword '{keyword}'",
                    "suggestion": "Try a different keyword or check spelling"
                }
            )
        
        total_scanned = len(apps_list)
        logger.info(f"[SEARCH_RESULT] TOTAL APPS FOUND: {total_scanned}")
        logger.info(f"[FILTERING] Filtering for score >= 3.0 AND score < 4.0...")
        
        # Clean and filter low-rated apps (< 3.5 for testing)
        low_rated_apps = []
        
        for app_data in apps_list:
            try:
                score = app_data.get('score')
                
                # Filter: score >= 3.0 AND score < 4.0 (apps in 3.0-4.0 rating range)
                if score is None or score == 0 or score < 3.0 or score >= 4.0:
                    continue
                
                if score >= 3.0 and score < 4.0:
                    low_rated_app = DeepScanAppInfo(
                        title=app_data.get('title', 'N/A'),
                        appId=app_data.get('appId', 'N/A'),
                        score=score,
                        developer=app_data.get('developer', 'N/A'),
                        description=app_data.get('summary', app_data.get('description', None)),
                        installs=app_data.get('installs', 'N/A')
                    )
                    low_rated_apps.append(low_rated_app)
            except Exception as e:
                logger.warning(f"[SKIP] Skipping app due to error: {str(e)}")
                continue
        
        # Sort by score (ascending - worst first)
        low_rated_apps.sort(key=lambda x: x.score)
        
        logger.info(f"[FILTER_RESULT] Found {len(low_rated_apps)} apps with rating 3.0-4.0")
        logger.info(f"[COMPLETE] Deep scan complete for '{keyword}': {len(low_rated_apps)} apps to return")
        
        return DeepScanResponse(
            keyword_searched=keyword,
            total_apps_scanned=total_scanned,
            low_rated_apps_count=len(low_rated_apps),
            apps=low_rated_apps
        )
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"[DEEP_SCAN_ERROR] ERROR during deep scan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to perform deep scan",
                "details": str(e),
                "keyword": keyword
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app_instance,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
