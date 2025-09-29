#!/usr/bin/env python3
"""
Genie Multi-Agent Tool for Healthcare Payor System
This module provides a LangChain-compatible tool for Genie integration using the working SDK method.
"""

import os
import json
from typing import Optional, Dict, Any, List
from databricks.sdk import WorkspaceClient
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class GenieQueryInput(BaseModel):
    """Input schema for Genie queries"""
    question: str = Field(description="The natural language question to ask Genie about the data")
    space_id: Optional[str] = Field(default=None, description="Genie space ID (uses default if not provided)")


class GenieMultiAgentTool(BaseTool):
    """LangChain tool for Genie integration using Databricks SDK"""
    
    name: str = "genie_query"
    description: str = (
        "Query structured data using natural language. "
        "Use this tool to ask questions about claims, members, providers, and other healthcare data. "
        "The tool will generate SQL queries and return structured results."
    )
    args_schema: type = GenieQueryInput
    space_id: str = "01f06a3068a81406a386e8eaefc74545"
    
    def __init__(self, space_id: str = "01f06a3068a81406a386e8eaefc74545", **kwargs):
        super().__init__(space_id=space_id, **kwargs)
        self._client = None
        self._genie_api = None
    
    def _get_client(self) -> WorkspaceClient:
        """Get or create Databricks client"""
        if self._client is None:
            os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT_azure'
            self._client = WorkspaceClient()
        return self._client
    
    def _get_genie_api(self):
        """Get or create Genie API client"""
        if self._genie_api is None:
            client = self._get_client()
            self._genie_api = client.genie
        return self._genie_api
    
    def _run(self, question: str, space_id: Optional[str] = None, **kwargs) -> str:
        """Execute Genie query and return results"""
        
        try:
            # Use provided space_id or default
            target_space_id = space_id or self.space_id
            
            print(f"🔮 Genie Query: {question}")
            print(f"Space ID: {target_space_id}")
            
            # Get Genie API client
            genie_api = self._get_genie_api()
            
            # Start conversation and wait for completion
            message = genie_api.start_conversation_and_wait(target_space_id, question)
            
            print(f"✅ Genie response received (Status: {message.status})")
            
            # Process the response
            result = {
                "question": question,
                "status": str(message.status),
                "conversation_id": message.conversation_id,
                "message_id": message.id,
                "results": []
            }
            
            # Get query results if attachments exist
            if message.attachments:
                print(f"📎 Processing {len(message.attachments)} attachments...")
                
                for i, attachment in enumerate(message.attachments):
                    attachment_result = {
                        "attachment_id": attachment.attachment_id,
                        "sql_query": None,
                        "description": None,
                        "data": []
                    }
                    
                    # Extract SQL query and description if available
                    if hasattr(attachment, 'query') and attachment.query:
                        attachment_result["sql_query"] = attachment.query.query
                        attachment_result["description"] = attachment.query.description
                        print(f"📝 SQL Query: {attachment.query.query}")
                    
                    # Get the actual query results
                    try:
                        query_results = genie_api.get_message_attachment_query_result(
                            target_space_id,
                            message.conversation_id,
                            message.id,
                            attachment.attachment_id
                        )
                        
                        # Extract data from results
                        if hasattr(query_results, 'statement_response') and query_results.statement_response:
                            result_data = query_results.statement_response.result
                            if hasattr(result_data, 'data_array') and result_data.data_array:
                                attachment_result["data"] = result_data.data_array
                                print(f"📊 Retrieved {len(result_data.data_array)} data rows")
                                
                                # Show column info if available
                                if hasattr(result_data, 'columns') and result_data.columns:
                                    columns = [col.name for col in result_data.columns]
                                    attachment_result["columns"] = columns
                                    print(f"📋 Columns: {columns}")
                        
                    except Exception as e:
                        print(f"⚠️ Error getting query results for attachment {i+1}: {e}")
                        attachment_result["error"] = str(e)
                    
                    result["results"].append(attachment_result)
            
            # Format the response for the agent
            response_text = self._format_response(result)
            print(f"✅ Genie tool execution completed")
            
            return response_text
            
        except Exception as e:
            error_msg = f"❌ Genie query failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """Format the Genie response for the agent"""
        
        response_parts = []
        
        # Add question and status
        response_parts.append(f"## 🔮 Genie Analysis")
        response_parts.append(f"**Query:** {result['question']}")
        response_parts.append(f"**Status:** {result['status']}")
        response_parts.append("")
        
        # Process each result
        for i, res in enumerate(result.get("results", [])):
            response_parts.append(f"### 📊 Result {i+1}")
            
            if res.get("sql_query"):
                response_parts.append(f"**SQL Query:**")
                response_parts.append(f"```sql\n{res['sql_query']}\n```")
            
            if res.get("description"):
                response_parts.append(f"**Description:** {res['description']}")
            
            if res.get("data"):
                response_parts.append(f"**Data ({len(res['data'])} rows):**")
                
                # Show data in a more structured way
                for j, row in enumerate(res['data'][:10]):  # Show first 10 rows
                    response_parts.append(f"• Row {j+1}: {row}")
                
                if len(res['data']) > 10:
                    response_parts.append(f"• ... and {len(res['data']) - 10} more rows")
            
            if res.get("error"):
                response_parts.append(f"**Error:** {res['error']}")
            
            response_parts.append("")
        
        return "\n".join(response_parts)


def create_genie_tool(space_id: str = "01f06a3068a81406a386e8eaefc74545") -> GenieMultiAgentTool:
    """Create a Genie tool instance"""
    return GenieMultiAgentTool(space_id=space_id)


# Test function
def test_genie_tool():
    """Test the Genie tool"""
    print("🧪 Testing Genie Multi-Agent Tool")
    print("=" * 50)
    
    tool = create_genie_tool()
    
    # Test query
    test_question = "What are the different statuses of claims and how many claims fall under each status?"
    print(f"Testing with question: {test_question}")
    
    result = tool._run(test_question)
    print("\n" + "=" * 50)
    print("RESULT:")
    print(result)


if __name__ == "__main__":
    test_genie_tool()
