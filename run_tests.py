#!/usr/bin/env python3
"""
Simple Test Runner for Multi-Agent Healthcare System
Run this to verify that the system is actually using AI agents.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test(test_name: str, test_file: str):
    """Run a specific test file"""
    print(f"\n🧪 Running {test_name}")
    print("-" * 50)
    
    try:
        # Run the test
        result = subprocess.run([
            "conda", "run", "-n", "azure_databricks", 
            "python", test_file
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Return success status
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {test_name}: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 MULTI-AGENT HEALTHCARE SYSTEM - TEST RUNNER")
    print("=" * 60)
    print("This script runs tests to verify the system is using real AI agents")
    print("=" * 60)
    
    # Define tests to run
    tests = [
        ("Agent Proof Test", "test_agents_proof.py"),
        ("Comprehensive Test Suite", "test_multiagent_system.py")
    ]
    
    results = []
    
    for test_name, test_file in tests:
        if os.path.exists(test_file):
            success = run_test(test_name, test_file)
            results.append((test_name, success))
        else:
            print(f"❌ Test file not found: {test_file}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Multi-agent system is working correctly!")
        print("✅ Real AI agents are being used!")
    else:
        print(f"\n❌ {total - passed} tests failed")
        print("🔧 Check the output above for details")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

