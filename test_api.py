"""
Example usage of the Play Store Scraper API

Run this script to test the API endpoints
"""

import requests
import json
from typing import Dict, List
import time

BASE_URL = "http://localhost:8000"


def print_section(title: str) -> None:
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_root_endpoint() -> None:
    """Test the root endpoint"""
    print_section("Testing Root Endpoint (GET /)")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Message: {data['message']}")
        print(f"Description: {data['description']}")
        print(f"Available Endpoints:")
        for endpoint, path in data['endpoints'].items():
            print(f"  - {endpoint}: {path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_health_endpoint() -> None:
    """Test the health check endpoint"""
    print_section("Testing Health Check (GET /health)")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Status: {data['status']}")
        print(f"Service: {data['service']}")
        print("✅ API is healthy!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_categories_endpoint() -> None:
    """Test the categories listing endpoint"""
    print_section("Testing Categories Endpoint (GET /categories)")
    
    try:
        response = requests.get(f"{BASE_URL}/categories")
        response.raise_for_status()
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Total Categories: {data['total_categories']}")
        print(f"\nApp Categories ({data['app_categories']['count']}):")
        print(f"  {', '.join(data['app_categories']['categories'][:5])}... (showing first 5)")
        print(f"\nGame Categories ({data['game_categories']['count']}):")
        print(f"  {', '.join(data['game_categories']['categories'][:5])}... (showing first 5)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_scrape_endpoint(category: str) -> None:
    """Test scraping a specific category"""
    print_section(f"Testing Scrape Endpoint (GET /scrape/{category})")
    
    try:
        print(f"Scraping category: '{category}'...")
        start_time = time.time()
        
        response = requests.get(f"{BASE_URL}/scrape/{category}", timeout=60)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Category: {data['category']}")
            print(f"Apps Found: {data['count']}")
            print(f"Scrape Time: {elapsed_time:.2f} seconds\n")
            
            print("Top 5 Apps:")
            for i, app in enumerate(data['apps'][:5], 1):
                print(f"\n{i}. {app['title']}")
                print(f"   Developer: {app['developer']}")
                print(f"   Rating: {app['score']}/5 ⭐" if app['score'] else "   Rating: N/A")
                print(f"   Price: {app['price']}")
                print(f"   App ID: {app['app_id']}")
        
        elif response.status_code == 404:
            error_data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Error: {error_data.get('detail', {}).get('error', 'Not found')}")
            
            suggestions = error_data.get('detail', {}).get('suggested_categories', [])
            if suggestions:
                print(f"\nSuggested Categories:")
                for cat in suggestions[:5]:
                    print(f"  - {cat}")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (may need to wait for Play Store response)")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the API running on {BASE_URL}?")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_invalid_category() -> None:
    """Test error handling with invalid category"""
    print_section("Testing Error Handling (Invalid Category)")
    
    try:
        response = requests.get(f"{BASE_URL}/scrape/invalid_category_xyz")
        
        if response.status_code == 404:
            error_data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Error Message: {error_data.get('detail', {}).get('error', '')}")
            
            suggestions = error_data.get('detail', {}).get('suggested_categories', [])
            if suggestions:
                print(f"\nSuggested Categories: {', '.join(suggestions[:3])}")
            print("✅ Error handling works correctly!")
        else:
            print(f"Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def run_all_tests() -> None:
    """Run all test cases"""
    print("\n" + "🚀 PLAY STORE SCRAPER API - TEST SUITE 🚀".center(60))
    
    # Test basic endpoints
    test_root_endpoint()
    test_health_endpoint()
    test_categories_endpoint()
    
    # Test error handling
    test_invalid_category()
    
    # Test scraping with a simple category
    print("\n" + "NOTE: Testing actual scraping may take 10-30 seconds".center(60))
    print("(Depends on network speed and Play Store response time)")
    
    test_categories = ["productivity", "action", "tools"]
    
    for category in test_categories:
        try:
            test_scrape_endpoint(category)
            break  # Only test one category to save time
        except:
            print(f"Skipping {category}...")
            continue
    
    # Summary
    print_section("✅ Test Suite Complete")
    print("For more detailed testing, visit the interactive documentation:")
    print(f"  → {BASE_URL}/docs")
    print()


if __name__ == "__main__":
    try:
        # Quick connectivity check
        print("Checking API connectivity...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ API is accessible\n")
            run_all_tests()
        else:
            print(f"❌ API returned status code {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {BASE_URL}")
        print("Make sure the server is running:")
        print("  python -m uvicorn backend.main:app_instance --port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
