#!/usr/bin/env python3
"""
Test script for Healthcare Payor UC Tools Integration
Tests the Databricks Unity Catalog functions and LangChain integration
"""

import os
import sys
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate

def test_databricks_connection():
    """Test Databricks workspace connection"""
    print("🔗 Testing Databricks connection...")
    try:
        client = WorkspaceClient(profile="DEFAULT")
        print("✅ Successfully connected to Databricks workspace")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Databricks: {e}")
        return False

def test_uc_tools():
    """Test Unity Catalog tools setup"""
    print("\n🛠️ Testing UC Tools setup...")
    try:
        catalog = "my_catalog"
        schema = "payer_silver"
        
        # Initialize UC Function Toolkit
        function_names = [
            f"{catalog}.{schema}.lookup_member",
            f"{catalog}.{schema}.lookup_claims", 
            f"{catalog}.{schema}.lookup_providers"
        ]
        
        toolkit = UCFunctionToolkit(function_names=function_names)
        tools = toolkit.tools
        
        print(f"✅ Successfully loaded {len(tools)} UC tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        return True, toolkit
        
    except Exception as e:
        print(f"❌ Failed to setup UC tools: {e}")
        print("Make sure UC functions are created in my_catalog.payer_silver")
        return False, None

def test_llm_connection():
    """Test LLM endpoint connection"""
    print("\n🤖 Testing LLM connection...")
    try:
        llm = ChatDatabricks(
            endpoint="databricks-meta-llama-3-3-70b-instruct", 
            temperature=0.1
        )
        
        # Simple test query
        response = llm.invoke("Hello, are you working?")
        print(f"✅ LLM response: {response.content[:100]}...")
        return True, llm
        
    except Exception as e:
        print(f"❌ Failed to connect to LLM: {e}")
        return False, None

def test_agent_creation(toolkit, llm):
    """Test agent creation with UC tools"""
    print("\n🎯 Testing agent creation...")
    try:
        # Define prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful Healthcare Payor AI Assistant."),
            ("human", "{input}"),
        ])
        
        # Create agent
        agent = create_tool_calling_agent(llm, toolkit.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=toolkit.tools, verbose=True)
        
        print("✅ Successfully created agent with UC tools")
        return True, agent_executor
        
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return False, None

def test_agent_queries(agent_executor):
    """Test agent with sample queries"""
    print("\n💬 Testing agent queries...")
    
    test_queries = [
        "Hello, can you help me with healthcare questions?",
        "Look up member M001",
        "Find cardiology providers",
        "What are the symptoms of diabetes?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            response = agent_executor.invoke({"input": query})
            print(f"✅ Response: {response['output'][:200]}...")
        except Exception as e:
            print(f"❌ Query failed: {e}")

def main():
    """Main test function"""
    print("🏥 Healthcare Payor UC Tools Integration Test")
    print("=" * 50)
    
    # Test 1: Databricks connection
    if not test_databricks_connection():
        print("\n❌ Test failed: Cannot connect to Databricks")
        return False
    
    # Test 2: UC Tools setup
    success, toolkit = test_uc_tools()
    if not success:
        print("\n❌ Test failed: UC tools not available")
        return False
    
    # Test 3: LLM connection
    success, llm = test_llm_connection()
    if not success:
        print("\n❌ Test failed: LLM not available")
        return False
    
    # Test 4: Agent creation
    success, agent_executor = test_agent_creation(toolkit, llm)
    if not success:
        print("\n❌ Test failed: Agent creation failed")
        return False
    
    # Test 5: Agent queries
    test_agent_queries(agent_executor)
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("1. Run the Streamlit app: streamlit run healthcare_payor_streamlit_app.py")
    print("2. Test the web interface")
    print("3. Verify UC functions in Databricks workspace")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
