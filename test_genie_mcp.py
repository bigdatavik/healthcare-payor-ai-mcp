#!/usr/bin/env python3
"""
Test script for Databricks Managed MCP Server - Genie Integration
This script tests the managed MCP server approach for Genie without making any changes to the main app.
"""

import os
import json
from databricks.sdk import WorkspaceClient

def test_genie_mcp_connection():
    """Test connection to Genie via managed MCP server"""
    
    print("🔮 Testing Databricks Managed MCP Server - Genie Integration")
    print("=" * 60)
    
    # Configuration
    workspace_url = "https://adb-984752964297111.11.azuredatabricks.net"
    genie_space_id = "01f06a3068a81406a386e8eaefc74545"
    genie_mcp_url = f"{workspace_url}/api/2.0/mcp/genie/{genie_space_id}"
    
    print(f"Workspace: {workspace_url}")
    print(f"Genie Space ID: {genie_space_id}")
    print(f"MCP Server URL: {genie_mcp_url}")
    print()
    
    try:
        # Step 1: Initialize Databricks client
        print("Step 1: Initializing Databricks client...")
        os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT_azure'
        workspace_client = WorkspaceClient()
        
        print(f"✅ Client initialized successfully")
        print(f"Host: {workspace_client.config.host}")
        print(f"Profile: {workspace_client.config.profile}")
        print()
        
        # Step 2: Test MCP client connection
        print("Step 2: Testing MCP client connection...")
        
        # Try to import the MCP client using standard MCP approach
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            print("✅ MCP library available")
        except ImportError as e:
            print(f"❌ MCP library not available: {e}")
            print("Installing MCP...")
            import subprocess
            subprocess.run(["pip", "install", "mcp"], check=True)
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            print("✅ MCP installed and imported")
        
        print("✅ MCP client libraries available")
        print()
        
        # Step 3: List available tools
        print("Step 3: Listing available Genie tools...")
        try:
            tools = mcp_client.list_tools()
            print(f"✅ Found {len(tools)} tools:")
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool.name}: {tool.description}")
            print()
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return False
        
        # Step 4: Test a simple query
        print("Step 4: Testing Genie query...")
        test_question = "What is the distribution of total charges for claims?"
        print(f"Question: {test_question}")
        
        try:
            # Find the appropriate tool name
            tool_name = None
            for tool in tools:
                if "query" in tool.name.lower() or "genie" in tool.name.lower():
                    tool_name = tool.name
                    break
            
            if not tool_name:
                print("❌ No suitable tool found for Genie queries")
                return False
            
            print(f"Using tool: {tool_name}")
            
            # Call the tool
            result = mcp_client.call_tool(tool_name, {"question": test_question})
            print("✅ Genie query successful!")
            print(f"Result: {json.dumps(result, indent=2)}")
            print()
            
        except Exception as e:
            print(f"❌ Error calling Genie tool: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 5: Test another query
        print("Step 5: Testing another query...")
        test_question_2 = "Show me the top 5 claims by amount"
        print(f"Question: {test_question_2}")
        
        try:
            result_2 = mcp_client.call_tool(tool_name, {"question": test_question_2})
            print("✅ Second Genie query successful!")
            print(f"Result: {json.dumps(result_2, indent=2)}")
            print()
            
        except Exception as e:
            print(f"❌ Error calling second Genie tool: {e}")
            return False
        
        print("🎉 All tests passed! Managed MCP server integration is working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alternative_approach():
    """Test alternative approach using direct API calls"""
    
    print("\n" + "=" * 60)
    print("🔄 Testing Alternative Approach - Direct API Calls")
    print("=" * 60)
    
    try:
        # Test the SDK method we know works
        from databricks.sdk import WorkspaceClient
        
        os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT_azure'
        client = WorkspaceClient()
        
        space_id = "01f06a3068a81406a386e8eaefc74545"
        test_question = "What is the distribution of total charges for claims?"
        
        print(f"Testing SDK method with question: {test_question}")
        
        # Use the SDK method we know works
        genie_api = client.genie
        message = genie_api.start_conversation_and_wait(space_id, test_question)
        
        print(f"✅ SDK method successful!")
        print(f"Status: {message.status}")
        print(f"Conversation ID: {message.conversation_id}")
        print(f"Message ID: {message.id}")
        
        if message.attachments:
            print(f"Found {len(message.attachments)} attachments")
            for i, attachment in enumerate(message.attachments):
                print(f"Attachment {i+1}: {attachment.type} - {attachment.attachment_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative approach failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Genie MCP Integration Tests")
    print("=" * 60)
    
    # Test 1: Managed MCP Server approach
    mcp_success = test_genie_mcp_connection()
    
    # Test 2: Alternative SDK approach (for comparison)
    sdk_success = test_alternative_approach()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Managed MCP Server: {'✅ SUCCESS' if mcp_success else '❌ FAILED'}")
    print(f"SDK Method: {'✅ SUCCESS' if sdk_success else '❌ FAILED'}")
    
    if mcp_success:
        print("\n🎉 Managed MCP server approach is working!")
        print("You can proceed with integrating this into your main application.")
    elif sdk_success:
        print("\n⚠️  Managed MCP server failed, but SDK method works.")
        print("You may need to use the SDK approach or troubleshoot MCP setup.")
    else:
        print("\n❌ Both approaches failed. Check your Databricks configuration.")
