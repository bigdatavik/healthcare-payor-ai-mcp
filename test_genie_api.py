#!/usr/bin/env python3
"""
Test script to learn and test Databricks Genie API connection
Based on Microsoft documentation: https://learn.microsoft.com/en-us/azure/databricks/genie/conversation-api
"""

import os
import requests
import json
import time
from databricks.sdk import WorkspaceClient

def get_databricks_token():
    """Get Databricks token from DEFAULT_azure profile"""
    try:
        # Initialize WorkspaceClient with DEFAULT_azure profile
        os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT_azure'
        client = WorkspaceClient()
        
        # Get token from the client
        token = client.config.token
        if token:
            print(f"✅ Got token from DEFAULT_azure profile: {token[:10]}...")
            return token
        else:
            print("❌ No token found in DEFAULT_azure profile")
            return None
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        return None

def test_genie_api():
    """Test Genie API connection and query"""
    
    # Configuration
    workspace_url = "https://adb-984752964297111.11.azuredatabricks.net"
    space_id = "01f06a3068a81406a386e8eaefc74545"
    test_question = "What is the distribution of total charges for claims?"
    
    print("🔮 Testing Databricks Genie API Connection")
    print("=" * 50)
    print(f"Workspace: {workspace_url}")
    print(f"Space ID: {space_id}")
    print(f"Test Question: {test_question}")
    print()
    
    # Step 1: Get authentication token
    print("Step 1: Getting authentication token...")
    token = get_databricks_token()
    if not token:
        print("❌ Failed to get authentication token")
        return False
    
    # Step 2: Start a conversation
    print("\nStep 2: Starting Genie conversation...")
    start_conversation_url = f"{workspace_url}/api/2.0/genie/spaces/{space_id}/start-conversation"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "content": test_question
    }
    
    print(f"🌐 Making request to: {start_conversation_url}")
    print(f"📤 Headers: {headers}")
    print(f"📤 Payload: {payload}")
    
    try:
        response = requests.post(start_conversation_url, headers=headers, json=payload, timeout=30)
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            conversation_data = response.json()
            print("✅ Conversation started successfully!")
            print(f"📋 Response: {json.dumps(conversation_data, indent=2)}")
            
            # Extract conversation and message IDs
            conversation_id = conversation_data.get('conversation', {}).get('id')
            message_id = conversation_data.get('message', {}).get('id')
            
            if conversation_id and message_id:
                print(f"✅ Conversation ID: {conversation_id}")
                print(f"✅ Message ID: {message_id}")
                
                # Step 3: Poll for completion
                print("\nStep 3: Polling for message completion...")
                return poll_message_status(workspace_url, space_id, conversation_id, message_id, token)
            else:
                print("❌ Could not extract conversation or message ID")
                return False
        else:
            print(f"❌ API call failed: {response.status_code} {response.reason}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def poll_message_status(workspace_url, space_id, conversation_id, message_id, token):
    """Poll for message completion status"""
    
    get_message_url = f"{workspace_url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"🔄 Polling message status...")
    print(f"🌐 URL: {get_message_url}")
    
    max_attempts = 12  # Poll for up to 2 minutes (12 * 10 seconds)
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(get_message_url, headers=headers, timeout=30)
            print(f"📥 Attempt {attempt + 1}: Status {response.status_code}")
            
            if response.status_code == 200:
                message_data = response.json()
                status = message_data.get('status', 'UNKNOWN')
                print(f"📊 Message status: {status}")
                
                if status == 'COMPLETED':
                    print("✅ Message completed successfully!")
                    print(f"📋 Full response: {json.dumps(message_data, indent=2)}")
                    
                    # Check for attachments (query results)
                    attachments = message_data.get('attachments', [])
                    if attachments:
                        print(f"📎 Found {len(attachments)} attachments")
                        for i, attachment in enumerate(attachments):
                            print(f"📎 Attachment {i+1}: {json.dumps(attachment, indent=2)}")
                            
                            # Try to get query results if attachment_id exists
                            attachment_id = attachment.get('attachment_id')
                            if attachment_id:
                                get_query_results(workspace_url, space_id, conversation_id, message_id, attachment_id, token)
                    else:
                        print("📎 No attachments found")
                    
                    return True
                elif status == 'FAILED':
                    print("❌ Message failed")
                    error = message_data.get('error')
                    if error:
                        print(f"❌ Error: {error}")
                    return False
                elif status == 'CANCELLED':
                    print("⚠️ Message was cancelled")
                    return False
                else:
                    print(f"⏳ Status: {status}, waiting...")
                    time.sleep(10)  # Wait 10 seconds before next poll
                    attempt += 1
            else:
                print(f"❌ Polling failed: {response.status_code} {response.reason}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Polling request failed: {e}")
            return False
    
    print("⏰ Timeout: Message did not complete within 2 minutes")
    return False

def get_query_results(workspace_url, space_id, conversation_id, message_id, attachment_id, token):
    """Get query results for an attachment"""
    
    query_results_url = f"{workspace_url}/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}"
    headers = {'Authorization': f'Bearer {token}'}
    
    print(f"\n🔍 Getting query results...")
    print(f"🌐 URL: {query_results_url}")
    
    try:
        response = requests.get(query_results_url, headers=headers, timeout=30)
        print(f"📥 Query results status: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Query results retrieved successfully!")
            print(f"📊 Results: {json.dumps(results, indent=2)}")
        else:
            print(f"❌ Failed to get query results: {response.status_code} {response.reason}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Query results request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Genie API Test")
    print("Based on Microsoft documentation: https://learn.microsoft.com/en-us/azure/databricks/genie/conversation-api")
    print()
    
    success = test_genie_api()
    
    if success:
        print("\n🎉 Genie API test completed successfully!")
    else:
        print("\n❌ Genie API test failed")
