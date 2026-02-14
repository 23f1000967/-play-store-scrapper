# 🚀 Quick Start Guide

## Installation & Setup (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python -m uvicorn backend.main:app_instance --host 0.0.0.0 --port 8000

# 3. Open in browser
# Visit: http://localhost:8000/docs
```

## ✨ What You Get

A professional FastAPI backend for scraping the US Google Play Store with:

- **49 Play Store Categories** - Apps & Games
- **Clean REST API** - Dynamic endpoints with error handling
- **Pydantic Validation** - Type-safe responses
- **Interactive Docs** - Auto-generated Swagger UI
- **Production Ready** - Logging, error handling, best practices

## 📌 Key Endpoints

| URL | What it does |
|-----|-------------|
| `GET /` | Welcome & instructions |
| `GET /docs` | **Interactive API documentation** ⭐ |
| `GET /scrape/action` | Scrape action games |
| `GET /scrape/productivity` | Scrape productivity apps |
| `GET /categories` | List all 49 categories |
| `GET /health` | API status check |

## 💡 Example Requests

### Using Browser
```
http://localhost:8000/scrape/productivity
http://localhost:8000/scrape/action
http://localhost:8000/categories
```

### Using curl
```bash
curl http://localhost:8000/scrape/action
curl http://localhost:8000/categories
curl http://localhost:8000/health
```

### Using Python
```python
import requests

response = requests.get("http://localhost:8000/scrape/productivity")
data = response.json()

for app in data['apps']:
    print(f"{app['title']} by {app['developer']}")
```

## 🎮 Available Categories

**Games:** action, adventure, arcade, board, card, casual, puzzle, racing, strategy...

**Apps:** productivity, business, health, finance, education, tools, travel...

See full list with: `GET /categories`

## 📚 Documentation Files

- **README.md** - Complete guide with examples
- **IMPLEMENTATION.md** - Technical details
- **/docs** - Interactive Swagger UI (when server running)

## 🔧 Configuration

Edit `backend/config.py` to customize:
- Server port
- Scraper settings (country, language, count)
- API title/version

## ❓ Troubleshooting

**Port 8000 already in use?**
```bash
python -m uvicorn backend.main:app_instance --port 8001
```

**API not responding?**
```bash
# Verify Python and packages
python --version
pip list | grep fastapi
```

**Need to stop the server?**
```
Press Ctrl+C in the terminal
```

## 📖 Full Documentation

For complete documentation including:
- All 49 categories
- Response formats
- Error handling
- Performance tips
- Production deployment

See **README.md**

---

**You're all set! 🎉**

Visit **http://localhost:8000/docs** to start using the API.
