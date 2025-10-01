"""
Unity Catalog Functions MCP Server Integration for Healthcare Payor AI System
Implements managed MCP server for UC functions
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import streamlit as st

class UCFunctionsMCPClient:
    """Client for interacting with Unity Catalog Functions managed MCP server"""
    
    def __init__(self, workspace_hostname: str, catalog: str, schema: str, profile: str = "DEFAULT_azure"):
        """
        Initialize UC Functions MCP client
        
        Args:
            workspace_hostname: Databricks workspace hostname
            catalog: Unity Catalog name
            schema: Schema name containing UC functions
            profile: Databricks CLI profile name
        """
        self.workspace_hostname = workspace_hostname
        self.catalog = catalog
        self.schema = schema
        self.profile = profile
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/functions/{catalog}/{schema}"
        
        # Initialize workspace client
        self.workspace_client = WorkspaceClient(profile=profile)
        
        # Initialize MCP client
        self.mcp_client = None
        self._initialize_mcp_client()
    
    def _initialize_mcp_client(self):
        """Initialize the MCP client connection"""
        try:
            self.mcp_client = DatabricksMCPClient(
                server_url=self.mcp_url,
                workspace_client=self.workspace_client
            )
            st.success(f"✅ Connected to UC Functions MCP server: {self.mcp_url}")
        except Exception as e:
            st.error(f"❌ Failed to connect to UC Functions MCP server: {e}")
            self.mcp_client = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available UC functions from MCP server"""
        if not self.mcp_client:
            return []
        
        try:
            tools = self.mcp_client.list_tools()
            return [{"name": tool.name, "description": tool.description} for tool in tools]
        except Exception as e:
            st.error(f"❌ Failed to list UC functions: {e}")
            return []
    
    def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a Unity Catalog function through MCP server or direct call
        
        Args:
            function_name: Name of the UC function to call
            **kwargs: Arguments for the function
            
        Returns:
            Dictionary containing function results
        """
        # Try MCP client first
        if self.mcp_client:
            try:
                result = self.mcp_client.call_tool(function_name, kwargs)
                
                return {
                    "success": True,
                    "function_name": function_name,
                    "arguments": kwargs,
                    "result": result.content if hasattr(result, 'content') else str(result),
                    "tool_used": "UC Functions MCP"
                }
            except Exception as e:
                st.info("ℹ️ UC Functions MCP server unavailable, trying direct database connection...")
        
        # Fallback to direct UC function call
        try:
            # Extract function name without catalog.schema prefix
            simple_function_name = function_name.split('__')[-1]
            full_function_name = f"{self.catalog}.{self.schema}.{simple_function_name}"
            
            # Call function directly
            result = self.workspace_client.functions.call_function(
                function_name=full_function_name,
                arguments=kwargs
            )
            
            return {
                "success": True,
                "function_name": function_name,
                "arguments": kwargs,
                "result": result,
                "tool_used": "UC Functions Direct"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unable to retrieve data from UC Functions. {str(e)}",
                "function_name": function_name,
                "arguments": kwargs,
                "tool_used": "UC Functions (Unavailable)"
            }
    
    def lookup_member(self, input_id: str) -> Dict[str, Any]:
        """Lookup member information using UC function"""
        function_name = f"{self.catalog}__{self.schema}__lookup_member"
        return self.call_function(function_name, input_id=input_id)
    
    def lookup_claims(self, member_id: str) -> Dict[str, Any]:
        """Lookup claims for a member using UC function"""
        function_name = f"{self.catalog}__{self.schema}__lookup_claims"
        return self.call_function(function_name, input_id=member_id)
    
    def lookup_providers(self, specialty_filter: str = None) -> Dict[str, Any]:
        """Lookup providers using UC function"""
        function_name = f"{self.catalog}__{self.schema}__lookup_providers"
        kwargs = {"specialty_filter": specialty_filter} if specialty_filter else {}
        return self.call_function(function_name, **kwargs)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of UC Functions MCP connection"""
        try:
            tools = self.list_tools()
            return {
                "status": "healthy" if tools else "unhealthy",
                "mcp_url": self.mcp_url,
                "catalog": self.catalog,
                "schema": self.schema,
                "functions_count": len(tools),
                "functions": [tool["name"] for tool in tools]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "mcp_url": self.mcp_url
            }

def create_uc_functions_tools_for_langchain(uc_client: UCFunctionsMCPClient):
    """
    Create LangChain tool wrappers for UC Functions MCP client
    
    Args:
        uc_client: Initialized UCFunctionsMCPClient instance
        
    Returns:
        List of LangChain tools for UC functions
    """
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
    
    class MemberLookupInput(BaseModel):
        input_id: str = Field(description="Member ID to lookup")
    
    class ClaimsLookupInput(BaseModel):
        member_id: str = Field(description="Member ID to lookup claims for")
    
    class ProvidersLookupInput(BaseModel):
        specialty_filter: str = Field(description="Provider specialty to filter by", default="")
    
    class UCMemberLookupTool(BaseTool):
        name: str = f"{uc_client.catalog}__{uc_client.schema}__lookup_member"
        description: str = f"Returns member information from {uc_client.catalog}.{uc_client.schema}.members table"
        args_schema: type[BaseModel] = MemberLookupInput
        
        def _run(self, input_id: str) -> str:
            result = uc_client.lookup_member(input_id)
            if result["success"]:
                return result["result"]
            else:
                return f"Error: {result['error']}"
    
    class UCClaimsLookupTool(BaseTool):
        name: str = f"{uc_client.catalog}__{uc_client.schema}__lookup_claims"
        description: str = f"Returns claims for a member from {uc_client.catalog}.{uc_client.schema}.claims table"
        args_schema: type[BaseModel] = ClaimsLookupInput
        
        def _run(self, member_id: str) -> str:
            result = uc_client.lookup_claims(member_id)
            if result["success"]:
                return result["result"]
            else:
                return f"Error: {result['error']}"
    
    class UCProvidersLookupTool(BaseTool):
        name: str = f"{uc_client.catalog}__{uc_client.schema}__lookup_providers"
        description: str = f"Returns providers by specialty from {uc_client.catalog}.{uc_client.schema}.providers table"
        args_schema: type[BaseModel] = ProvidersLookupInput
        
        def _run(self, specialty_filter: str = "") -> str:
            result = uc_client.lookup_providers(specialty_filter)
            if result["success"]:
                return result["result"]
            else:
                return f"Error: {result['error']}"
    
    return [UCMemberLookupTool(), UCClaimsLookupTool(), UCProvidersLookupTool()]

# Configuration
WORKSPACE_HOSTNAME = "adb-984752964297111.11.azuredatabricks.net"
CATALOG = "my_catalog"
SCHEMA = "payer_silver"
DATABRICKS_PROFILE = "DEFAULT_azure"

def get_uc_functions_mcp_client() -> UCFunctionsMCPClient:
    """Get initialized UC Functions MCP client"""
    return UCFunctionsMCPClient(
        workspace_hostname=WORKSPACE_HOSTNAME,
        catalog=CATALOG,
        schema=SCHEMA,
        profile=DATABRICKS_PROFILE
    )

# Test function
def test_uc_functions_connection():
    """Test UC Functions MCP connection"""
    print("🧪 Testing UC Functions MCP Connection...")
    
    client = get_uc_functions_mcp_client()
    health = client.get_health_status()
    
    print(f"Status: {health['status']}")
    print(f"MCP URL: {health['mcp_url']}")
    print(f"Catalog: {health['catalog']}, Schema: {health['schema']}")
    
    if health['status'] == 'healthy':
        print(f"Available functions: {health['functions']}")
        
        # Test member lookup
        result = client.lookup_member("1001")
        print(f"Member lookup test: {result}")
    else:
        print(f"Connection failed: {health.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_uc_functions_connection()
