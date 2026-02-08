"""
Test de validation complète du projet.
Vérifie que tous les modules se chargent correctement.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test all imports."""
    print("🧪 Testing imports...\n")
    
    tests = [
        ("Core Config", "from core.config import CONFIG"),
        ("Core Logger", "from core.logger import get_logger"),
        ("Core Cache", "from core.cache import cache"),
        ("Core Utils", "from core.utils import retry"),
        ("Models", "from models.tweet import Tweet, Trend"),
        ("Provider Router", "from providers.router import router"),
        ("Generator", "from agent.generator import generator"),
        ("Scorer", "from agent.scoring import scorer"),
        ("Remix Engine", "from agent.remix_engine import remix_engine"),
        ("Memory Engine", "from agent.memory_engine import memory_engine"),
        ("Orchestrator", "from agent.orchestrator import orchestrator"),
        ("Translator", "from agent.translator import translator"),
        ("Trend Analyzer", "from agent.trend_analyzer import analyzer"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)[:50]}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0


def test_config():
    """Test configuration loading."""
    print("⚙️  Testing configuration...\n")
    
    try:
        from core.config import CONFIG
        
        checks = [
            ("App name", CONFIG.app_name),
            ("API port", CONFIG.api_port),
            ("LLM Provider", CONFIG.llm.provider),
            ("Memory enabled", CONFIG.memory.enabled),
        ]
        
        for name, value in checks:
            print(f"✅ {name}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_logger():
    """Test logger."""
    print("\n📝 Testing logger...\n")
    
    try:
        from core.logger import get_logger
        
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ Logger working")
        return True
    except Exception as e:
        print(f"❌ Logger failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("  Editorial Agent IA - Validation Test")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config", test_config()))
    results.append(("Logger", test_logger()))
    
    print("\n" + "=" * 60)
    print("  Final Results")
    print("=" * 60)
    print()
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("✨ All tests passed! Application is ready to run.")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
