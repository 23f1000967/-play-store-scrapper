"""
Verify that all requirements are installed and working
"""

import sys
import importlib
from typing import List, Tuple

def check_package(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, '__version__', 'unknown')
        return True, version
    except ImportError:
        return False, "not installed"


def main():
    print("\n" + "="*60)
    print("  Play Store Scraper API - Requirements Check")
    print("="*60 + "\n")
    
    requirements = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("google-play-scraper", "google_play_scraper"),
        ("requests", "requests"),
    ]
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}\n")
    
    all_ok = True
    
    for package, import_name in requirements:
        ok, version = check_package(package, import_name)
        status = "✅" if ok else "❌"
        print(f"{status} {package:<25} {version}")
        if not ok:
            all_ok = False
    
    print("\n" + "="*60)
    
    if all_ok:
        print("✅ All requirements are installed!")
        print("\nYou can now start the API:")
        print("  python -m uvicorn backend.main:app_instance --port 8000")
        print("\nOr visit: http://localhost:8000/docs")
    else:
        print("❌ Some requirements are missing!")
        print("\nInstall them with:")
        print("  pip install -r requirements.txt")
    
    print("="*60 + "\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
