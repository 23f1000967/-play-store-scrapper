# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT REQUESTS                              │
│  (Browser, curl, Python, JavaScript, etc.)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  GET /                  → Welcome message                │  │
│  │  GET /health            → Status check                   │  │
│  │  GET /docs              → Swagger UI                     │  │
│  │  GET /categories        → List all 49 categories         │  │
│  │  GET /scrape/{category} → Main scraping endpoint         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │   Input Processing Layer       │
         │  ┌──────────────────────────┐  │
         │  │ • Lowercase conversion   │  │
         │  │ • Space → underscore     │  │
         │  │ • Validation             │  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │    CATEGORY_MAP (49 items)     │
         │  ┌──────────────────────────┐  │
         │  │  category → Play Store ID │  │
         │  │  "action" → "GAME_ACTION" │  │
         │  │  "prod..." → "PRODUCTIVITY"  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │   Google Play Scraper          │
         │  ┌──────────────────────────┐  │
         │  │ country='us'             │  │
         │  │ lang='en'                │  │
         │  │ count=50                 │  │
         │  │ sort=NEWEST              │  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │    Google Play Store (API)     │
         │   Returns raw app data         │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │    Response Cleaning           │
         │  ┌──────────────────────────┐  │
         │  │ Extract needed fields:   │  │
         │  │ • title                  │  │
         │  │ • appId                  │  │
         │  │ • score                  │  │
         │  │ • developer              │  │
         │  │ • price                  │  │
         │  │ • icon                   │  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────┐
         │    Pydantic Validation         │
         │  (AppInfo model)               │
         │  ┌──────────────────────────┐  │
         │  │ Type checking            │  │
         │  │ Field validation         │  │
         │  │ JSON serialization       │  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Clean JSON Response                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ {                                                        │  │
│  │   "category": "action",                                 │  │
│  │   "count": 50,                                          │  │
│  │   "apps": [                                             │  │
│  │     {                                                   │  │
│  │       "title": "...",                                  │  │
│  │       "app_id": "...",                                 │  │
│  │       "score": 4.5,                                    │  │
│  │       "developer": "...",                              │  │
│  │       "price": "Free",                                 │  │
│  │       "icon_url": "..."                                │  │
│  │     }                                                   │  │
│  │   ]                                                     │  │
│  │ }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │  CLIENT APP    │
                 └────────────────┘
```

## Error Handling Flow

```
Request with invalid category (e.g., "xyz")
            │
            ▼
        Input Processing
            │
            ▼
     Check CATEGORY_MAP
            │
        ┌───┴───┐
        │       │
        ▼       ▼
     Found    NOT FOUND
        │       │
        │       ▼
        │   Get Suggestions
        │       │
        │       ▼
        │   Return 404 with:
        │   • Error message
        │   • Suggested categories
        │   • Available count
        │
        └───────┬──────┘
                │
                ▼
          HTTP 404 Response
```

## Project Structure

```
backend/main.py
├── Imports (FastAPI, Pydantic, google-play-scraper)
│
├── CATEGORY_MAP Dictionary (49 items)
│   ├── App Categories (34)
│   └── Game Categories (15)
│
├── Pydantic Models
│   ├── AppInfo (response model)
│   ├── ScrapeResponse
│   └── ErrorResponse
│
├── FastAPI Application
│   ├── app_instance = FastAPI(...)
│   │
│   ├── @app.get("/")
│   │   └── Root endpoint
│   │
│   ├── @app.get("/health")
│   │   └── Health check
│   │
│   ├── @app.get("/scrape/{category_name}")
│   │   ├── Input normalization
│   │   ├── Category validation
│   │   ├── Scraping logic
│   │   ├── Response cleaning
│   │   └── Error handling
│   │
│   ├── @app.get("/categories")
│   │   └── Category listing
│   │
│   └── if __name__ == "__main__"
│       └── uvicorn.run(...)
```

## Data Flow Example

```
CLIENT REQUEST
│
└─→ GET /scrape/productivity
    │
    └─→ Input: "productivity"
        │
        └─→ Normalize: "productivity" (already normalized)
            │
            └─→ Check CATEGORY_MAP["productivity"]
                │
                └─→ Found: "PRODUCTIVITY"
                    │
                    └─→ Call google_play_scraper.app(
                        "PRODUCTIVITY",
                        country='us',
                        lang='en',
                        count=50,
                        sort=Sort.NEWEST
                    )
                    │
                    └─→ Receives raw app data (50 apps)
                        │
                        └─→ Clean response:
                            ├─ Extract title
                            ├─ Extract appId
                            ├─ Extract score
                            ├─ Extract developer
                            ├─ Extract price
                            └─ Extract icon
                            │
                            └─→ Create AppInfo objects
                                │
                                └─→ Validate with Pydantic
                                    │
                                    └─→ Return ScrapeResponse
                                        │
                                        └─→ JSON to CLIENT
                                            │
                                            └─→ Status 200 OK
```

## Categories Distribution

```
ALL CATEGORIES (49 total)
│
├─ APP CATEGORIES (34)
│  │
│  ├─ Productivity (1)
│  │  └─ productivity
│  │
│  ├─ Business & Work (2)
│  │  ├─ business
│  │  └─ work
│  │
│  ├─ Communication (1)
│  │  └─ communication
│  │
│  ├─ Social & Entertainment (3)
│  │  ├─ social
│  │  ├─ entertainment
│  │  └─ news
│  │
│  ├─ Media & Content (5)
│  │  ├─ books
│  │  ├─ comics
│  │  ├─ music
│  │  ├─ video
│  │  └─ photography
│  │
│  ├─ Lifestyle (8)
│  │  ├─ lifestyle
│  │  ├─ health
│  │  ├─ beauty
│  │  ├─ food
│  │  ├─ travel
│  │  ├─ shopping
│  │  ├─ maps
│  │  └─ weather
│  │
│  ├─ Reference & Education (4)
│  │  ├─ education
│  │  ├─ books (shared)
│  │  ├─ libraries
│  │  └─ medical
│  │
│  ├─ Personalization & Tools (4)
│  │  ├─ tools
│  │  ├─ personalization
│  │  ├─ auto
│  │  └─ house
│  │
│  ├─ Family & Events (2)
│  │  ├─ parenting
│  │  └─ events
│  │
│  └─ Art & Design (1)
│     └─ art_design
│
└─ GAME CATEGORIES (15)
   │
   ├─ Action Games (3)
   │  ├─ action
   │  ├─ adventure
   │  └─ arcade
   │
   ├─ Strategy Games (3)
   │  ├─ strategy
   │  ├─ puzzle
   │  └─ board
   │
   ├─ Sports Games (2)
   │  ├─ sports_game
   │  └─ racing
   │
   ├─ RPG & Simulation (2)
   │  ├─ role_playing
   │  └─ simulation
   │
   ├─ Casual Games (3)
   │  ├─ casual
   │  ├─ card
   │  └─ trivia
   │
   └─ Other Games (2)
      ├─ educational_game
      └─ music_game
```

---

**Architecture Version**: 1.0  
**Last Updated**: February 11, 2026  
**Status**: ✅ Complete
