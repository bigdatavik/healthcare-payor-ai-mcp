#!/usr/bin/env python3
"""
Simple test script for Databricks Managed MCP Server - Genie Integration
This script tests the managed MCP server approach using direct HTTP requests.
"""

import os
import json
import requests
from databricks.sdk import WorkspaceClient

def test_genie_mcp_http():
    """Test Genie MCP server using direct HTTP requests"""
    
    print("🔮 Testing Databricks Managed MCP Server - Genie Integration (HTTP)")
    print("=" * 70)
    
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
        
        # Step 2: Get authentication token
        print("Step 2: Getting authentication token...")
        token = workspace_client.config.token
        if not token:
            print("❌ No token found in workspace client")
            return False
        
        print(f"✅ Token obtained: {token[:10]}...")
        print()
        
        # Step 3: Test MCP server endpoint
        print("Step 3: Testing MCP server endpoint...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test if the MCP server endpoint is accessible
        try:
            # Try to get server info or list tools
            response = requests.get(genie_mcp_url, headers=headers, timeout=30)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ MCP server endpoint is accessible!")
                try:
                    response_json = response.json()
                    print(f"Response: {json.dumps(response_json, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
            else:
                print(f"❌ MCP server returned status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing MCP server: {e}")
            return False
        
        print()
        
        # Step 4: Test with POST request (if needed)
        print("Step 4: Testing MCP server with POST request...")
        test_payload = {
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = requests.post(genie_mcp_url, headers=headers, json=test_payload, timeout=30)
            print(f"POST Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ MCP server POST request successful!")
                try:
                    response_json = response.json()
                    print(f"POST Response: {json.dumps(response_json, indent=2)}")
                except:
                    print(f"POST Response text: {response.text}")
            else:
                print(f"❌ MCP server POST returned status {response.status_code}")
                print(f"POST Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error with POST request: {e}")
            return False
        
        print()
        print("🎉 MCP server endpoint is working!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sdk_method():
    """Test the SDK method we know works for comparison"""
    
    print("\n" + "=" * 70)
    print("🔄 Testing SDK Method (Known Working)")
    print("=" * 70)
    
    try:
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
                print(f"Attachment {i+1}: {attachment.attachment_id}")
                
                # Try to get query results
                try:
                    query_results = genie_api.get_message_attachment_query_result(
                        space_id,
                        message.conversation_id,
                        message.id,
                        attachment.attachment_id
                    )
                    print(f"Query results retrieved successfully!")
                    if hasattr(query_results, 'statement_response') and query_results.statement_response:
                        result = query_results.statement_response.result
                        if hasattr(result, 'data_array') and result.data_array:
                            print(f"Data rows: {len(result.data_array)}")
                            for j, row in enumerate(result.data_array[:3]):  # Show first 3 rows
                                print(f"Row {j+1}: {row}")
                except Exception as e:
                    print(f"Error getting query results: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SDK method failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Genie MCP Integration Tests (Simple HTTP)")
    print("=" * 70)
    
    # Test 1: Managed MCP Server HTTP approach
    mcp_success = test_genie_mcp_http()
    
    # Test 2: SDK method (for comparison)
    sdk_success = test_sdk_method()
    
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    print(f"Managed MCP Server (HTTP): {'✅ SUCCESS' if mcp_success else '❌ FAILED'}")
    print(f"SDK Method: {'✅ SUCCESS' if sdk_success else '❌ FAILED'}")
    
    if mcp_success:
        print("\n🎉 Managed MCP server endpoint is accessible!")
        print("You can proceed with integrating this into your main application.")
    elif sdk_success:
        print("\n⚠️  Managed MCP server failed, but SDK method works.")
        print("You may need to use the SDK approach or troubleshoot MCP setup.")
    else:
        print("\n❌ Both approaches failed. Check your Databricks configuration.")
