"""
Genie MCP Server Integration for Healthcare Payor AI System
Implements managed MCP server for Genie space queries
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient
import streamlit as st

class GenieMCPClient:
    """Client for interacting with Genie managed MCP server"""
    
    def __init__(self, workspace_hostname: str, genie_space_id: str, profile: str = "DEFAULT_azure"):
        """
        Initialize Genie MCP client
        
        Args:
            workspace_hostname: Databricks workspace hostname
            genie_space_id: Genie space ID
            profile: Databricks CLI profile name
        """
        self.workspace_hostname = workspace_hostname
        self.genie_space_id = genie_space_id
        self.profile = profile
        self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
        
        # Initialize workspace client
        self.workspace_client = WorkspaceClient(profile=profile)
        
        # In cloud environments, get hostname from workspace client if not provided
        if not workspace_hostname or workspace_hostname == "auto-detect":
            try:
                # Try to get hostname from workspace client (works in cloud environments)
                self.workspace_hostname = self.workspace_client.config.host
                self.mcp_url = f"https://{self.workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
            except:
                # Fallback to provided hostname
                self.workspace_hostname = workspace_hostname
                self.mcp_url = f"https://{workspace_hostname}/api/2.0/mcp/genie/{genie_space_id}"
        
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
            st.success(f"✅ Connected to Genie MCP server: {self.mcp_url}")
        except Exception as e:
            st.error(f"❌ Failed to connect to Genie MCP server: {e}")
            self.mcp_client = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from Genie MCP server"""
        if not self.mcp_client:
            return []
        
        try:
            tools = self.mcp_client.list_tools()
            return [{"name": tool.name, "description": tool.description} for tool in tools]
        except Exception as e:
            st.error(f"❌ Failed to list Genie tools: {e}")
            return []
    
    def query_genie(self, query: str) -> Dict[str, Any]:
        """
        Query Genie space using natural language
        
        Args:
            query: Natural language query for Genie
            
        Returns:
            Dictionary containing query results
        """
        if not self.mcp_client:
            return {"error": "MCP client not initialized"}
        
        try:
            # Use the genie_query tool from MCP server
            result = self.mcp_client.call_tool("genie_query", {"query": query})
            
            return {
                "success": True,
                "query": query,
                "result": result.content if hasattr(result, 'content') else str(result),
                "tool_used": "Genie MCP"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "tool_used": "Genie MCP"
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of Genie MCP connection"""
        try:
            tools = self.list_tools()
            return {
                "status": "healthy" if tools else "unhealthy",
                "mcp_url": self.mcp_url,
                "tools_count": len(tools),
                "tools": [tool["name"] for tool in tools]
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "mcp_url": self.mcp_url
            }

def create_genie_tool_for_langchain(genie_client: GenieMCPClient):
    """
    Create a LangChain tool wrapper for Genie MCP client
    
    Args:
        genie_client: Initialized GenieMCPClient instance
        
    Returns:
        LangChain tool for Genie queries
    """
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
    
    class GenieQueryInput(BaseModel):
        query: str = Field(description="Natural language query for Genie space")
    
    class GenieMCPTool(BaseTool):
        name: str = "genie_mcp_query"
        description: str = """Query structured data using natural language through Genie MCP server. 
        Use this tool to analyze data, get insights, and answer questions about structured data tables.
        This tool connects to the managed Genie MCP server for advanced data analysis."""
        args_schema: type[BaseModel] = GenieQueryInput
        
        def _run(self, query: str) -> str:
            """Execute Genie query through MCP server"""
            result = genie_client.query_genie(query)
            
            if result["success"]:
                return f"Genie Analysis:\n{result['result']}"
            else:
                return f"Error querying Genie: {result['error']}"
    
    return GenieMCPTool()

# Configuration - Import from config.py
try:
    from config import WORKSPACE_HOSTNAME, DATABRICKS_PROFILE, GENIE_SPACE_ID
except ImportError:
    # Fallback values if importing fails
    WORKSPACE_HOSTNAME = "adb-984752964297111.11.azuredatabricks.net"
    GENIE_SPACE_ID = "01f06a3068a81406a386e8eaefc74545"
    DATABRICKS_PROFILE = "DEFAULT_azure"

def get_genie_mcp_client() -> GenieMCPClient:
    """Get initialized Genie MCP client"""
    return GenieMCPClient(
        workspace_hostname=WORKSPACE_HOSTNAME,
        genie_space_id=GENIE_SPACE_ID,
        profile=DATABRICKS_PROFILE
    )

# Test function
def test_genie_connection():
    """Test Genie MCP connection"""
    print("🧪 Testing Genie MCP Connection...")
    
    client = get_genie_mcp_client()
    health = client.get_health_status()
    
    print(f"Status: {health['status']}")
    print(f"MCP URL: {health['mcp_url']}")
    
    if health['status'] == 'healthy':
        print(f"Available tools: {health['tools']}")
        
        # Test a simple query
        test_query = "What tables are available in this space?"
        result = client.query_genie(test_query)
        print(f"Test query result: {result}")
    else:
        print(f"Connection failed: {health.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_genie_connection()
