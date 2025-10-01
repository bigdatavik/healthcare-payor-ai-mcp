#!/usr/bin/env python3
"""
Healthcare Payor AI System - Demo Script
Automated demo script to showcase MCP integration capabilities
"""

import time
import requests
import json
from typing import Dict, List, Any

class HealthcarePayorDemo:
    """Automated demo script for Healthcare Payor AI System"""
    
    def __init__(self, base_url: str = "http://localhost:8503"):
        self.base_url = base_url
        self.demo_queries = self._setup_demo_queries()
    
    def _setup_demo_queries(self) -> Dict[str, List[str]]:
        """Setup demo queries for each tool"""
        return {
            "genie": [
                "What tables are available in the database?",
                "Show me the top 5 claims by amount",
                "What is the total claims cost for this quarter?",
                "Show me member demographics by age group",
                "What are the most common procedure codes?"
            ],
            "uc_functions": [
                "Lookup member information for member ID 1001",
                "Find all claims for member ID 1001 in the last 6 months",
                "Search for cardiology providers in New York",
                "Check member eligibility for member ID 2001",
                "Show provider network coverage for zip code 10001"
            ],
            "knowledge_assistant": [
                "What are the billing codes for cardiology procedures?",
                "What is our policy on pre-authorization for MRI scans?",
                "What are the HIPAA requirements for member data access?",
                "What are the CPT codes for emergency room visits?",
                "What is our policy on out-of-network coverage?"
            ]
        }
    
    def check_system_status(self) -> bool:
        """Check if the system is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_demo_query(self, query: str, tool_type: str) -> Dict[str, Any]:
        """Run a demo query and return results"""
        # This would integrate with the actual Streamlit app API
        # For now, we'll simulate the response
        return {
            "query": query,
            "tool_type": tool_type,
            "status": "success",
            "response": f"Demo response for {tool_type}: {query}",
            "timestamp": time.time()
        }
    
    def run_quick_demo(self) -> None:
        """Run a 5-minute quick demo"""
        print("🏥 Healthcare Payor AI System - Quick Demo")
        print("=" * 50)
        
        # Check system status
        print("🔍 Checking system status...")
        if not self.check_system_status():
            print("❌ System not available. Please start the app first.")
            return
        
        print("✅ System is running and healthy")
        print()
        
        # Demo each tool
        for tool, queries in self.demo_queries.items():
            print(f"🛠️  {tool.upper()} Demo:")
            print("-" * 30)
            
            for i, query in enumerate(queries[:2], 1):  # Show first 2 queries
                print(f"  {i}. Query: {query}")
                result = self.run_demo_query(query, tool)
                print(f"     Response: {result['response']}")
                print()
                time.sleep(1)  # Pause for readability
        
        print("🎉 Quick demo completed!")
        print(f"🌐 Open the full app at: {self.base_url}")
    
    def run_full_demo(self) -> None:
        """Run a comprehensive 15-minute demo"""
        print("🏥 Healthcare Payor AI System - Full Demo")
        print("=" * 50)
        
        # System overview
        print("📊 System Overview:")
        print("- Genie MCP Server: Data Analytics & Reporting")
        print("- UC Functions MCP Server: Member & Claims Lookup")
        print("- Knowledge Assistant: Document Analysis & Policy Search")
        print()
        
        # Run all demo queries
        for tool, queries in self.demo_queries.items():
            print(f"🛠️  {tool.upper()} Comprehensive Demo:")
            print("-" * 40)
            
            for i, query in enumerate(queries, 1):
                print(f"  {i}. Query: {query}")
                result = self.run_demo_query(query, tool)
                print(f"     Response: {result['response']}")
                print()
                time.sleep(2)  # Longer pause for full demo
        
        print("🎉 Full demo completed!")
        print(f"🌐 Open the full app at: {self.base_url}")
    
    def run_scenario_demo(self, scenario: str) -> None:
        """Run a specific scenario demo"""
        scenarios = {
            "member_inquiry": [
                "Find member Sarah Johnson, member ID 2001",
                "Show recent claims for this member",
                "What is her current coverage plan?",
                "What is our policy on out-of-network coverage?"
            ],
            "claims_processing": [
                "Show me pending claims for review",
                "Verify member eligibility for claim 12345",
                "Is this provider in our network?",
                "Does this procedure require pre-authorization?"
            ],
            "analytics_report": [
                "What are our total claims costs this quarter?",
                "How do costs compare to last quarter?",
                "What is our member satisfaction trend?",
                "Which providers have the highest utilization?"
            ]
        }
        
        if scenario not in scenarios:
            print(f"❌ Unknown scenario: {scenario}")
            print(f"Available scenarios: {list(scenarios.keys())}")
            return
        
        print(f"🎭 Scenario Demo: {scenario.replace('_', ' ').title()}")
        print("=" * 50)
        
        for i, query in enumerate(scenarios[scenario], 1):
            print(f"  {i}. Query: {query}")
            result = self.run_demo_query(query, "scenario")
            print(f"     Response: {result['response']}")
            print()
            time.sleep(2)
        
        print("🎉 Scenario demo completed!")

def main():
    """Main demo function"""
    demo = HealthcarePayorDemo()
    
    print("🏥 Healthcare Payor AI System - Demo Script")
    print("=" * 50)
    print("1. Quick Demo (5 minutes)")
    print("2. Full Demo (15 minutes)")
    print("3. Member Inquiry Scenario")
    print("4. Claims Processing Scenario")
    print("5. Analytics Report Scenario")
    print("6. Exit")
    print()
    
    while True:
        choice = input("Select demo option (1-6): ").strip()
        
        if choice == "1":
            demo.run_quick_demo()
        elif choice == "2":
            demo.run_full_demo()
        elif choice == "3":
            demo.run_scenario_demo("member_inquiry")
        elif choice == "4":
            demo.run_scenario_demo("claims_processing")
        elif choice == "5":
            demo.run_scenario_demo("analytics_report")
        elif choice == "6":
            print("👋 Demo script ended. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
