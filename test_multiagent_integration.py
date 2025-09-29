#!/usr/bin/env python3
"""
Test script for Multi-Agent Genie Integration
This script tests the complete multi-agent system integration.
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_genie_tool():
    """Test the Genie tool"""
    print("🧪 Testing Genie Tool")
    print("=" * 40)
    
    try:
        from genie_multiagent_tool import create_genie_tool
        
        tool = create_genie_tool()
        test_question = "What are the different statuses of claims and how many claims fall under each status?"
        
        print(f"Testing question: {test_question}")
        result = tool._run(test_question)
        print(f"✅ Genie tool test successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Genie tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiagent_system():
    """Test the multi-agent system"""
    print("\n🧪 Testing Multi-Agent System")
    print("=" * 40)
    
    try:
        from langgraph_genie_multiagent import create_multiagent_system
        
        system = create_multiagent_system()
        test_question = "Show me the top 5 claims by amount"
        
        print(f"Testing question: {test_question}")
        result = system.process_query(test_question)
        print(f"✅ Multi-agent system test successful!")
        print(f"Result length: {len(result)} characters")
        print(f"First 200 chars: {result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-agent system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_imports():
    """Test that Streamlit app can import all components"""
    print("\n🧪 Testing Streamlit App Imports")
    print("=" * 40)
    
    try:
        # Test individual imports
        from genie_multiagent_tool import create_genie_tool
        print("✅ Genie tool import successful")
        
        from langgraph_genie_multiagent import create_multiagent_system
        print("✅ Multi-agent system import successful")
        
        # Test that we can create instances
        genie_tool = create_genie_tool()
        print("✅ Genie tool creation successful")
        
        multiagent_system = create_multiagent_system()
        print("✅ Multi-agent system creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit app import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Multi-Agent Genie Integration Tests")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Set up environment
    os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT_azure'
    
    # Run tests
    tests = [
        ("Genie Tool", test_genie_tool),
        ("Multi-Agent System", test_multiagent_system),
        ("Streamlit App Imports", test_streamlit_imports)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test...")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Multi-Agent Genie integration is ready!")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
