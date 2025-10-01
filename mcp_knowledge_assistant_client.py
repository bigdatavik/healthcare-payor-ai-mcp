"""
Knowledge Assistant MCP Server Integration for Healthcare Payor AI System
Implements Knowledge Assistant for unstructured text analysis
"""

import os
import json
from typing import Dict, List, Any, Optional
from databricks.sdk import WorkspaceClient
import streamlit as st
from openai import OpenAI

class KnowledgeAssistantMCPClient:
    """Client for Knowledge Assistant functionality"""
    
    def __init__(self, workspace_client: WorkspaceClient):
        """
        Initialize Knowledge Assistant client
        
        Args:
            workspace_client: Databricks workspace client
        """
        self.workspace_client = workspace_client
        self.knowledge_client = None
        self._setup_knowledge_client()
    
    def _setup_knowledge_client(self):
        """Setup the Knowledge Assistant client using token generation"""
        try:
            # Generate a token using the Databricks client
            import time
            token = self.workspace_client.tokens.create(
                comment=f"knowledge-assistant-{time.time_ns()}", 
                lifetime_seconds=3600
            )
            
            # Initialize OpenAI client for Knowledge Assistant
            self.knowledge_client = OpenAI(
                api_key=token.token_value,
                base_url="https://adb-984752964297111.11.azuredatabricks.net/serving-endpoints"
            )
            
            # Store token info for cleanup
            self._token_info = token.token_info
            st.success("✅ Knowledge Assistant client initialized")
        except Exception as e:
            st.warning(f"⚠️ Failed to setup Knowledge Assistant client: {e}")
            self.knowledge_client = None
    
    def query_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Query Knowledge Assistant for unstructured text analysis
        
        Args:
            query: Natural language query for knowledge analysis
            
        Returns:
            Dictionary containing query results
        """
        if not self.knowledge_client:
            return {
                "success": False,
                "error": "Knowledge Assistant client not initialized",
                "query": query,
                "tool_used": "Knowledge Assistant"
            }
        
        try:
            # Use the OpenAI client to query the Knowledge Assistant
            response = self.knowledge_client.responses.create(
                model="ka-d0808962-endpoint",
                input=[
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            )
            
            if response.output and len(response.output) > 0:
                return {
                    "success": True,
                    "query": query,
                    "result": response.output[0].content[0].text,
                    "tool_used": "Knowledge Assistant"
                }
            else:
                return {
                    "success": False,
                    "error": "No response from Knowledge Assistant",
                    "query": query,
                    "tool_used": "Knowledge Assistant"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "tool_used": "Knowledge Assistant"
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Check health status of Knowledge Assistant connection"""
        try:
            return {
                "status": "healthy" if self.knowledge_client else "unhealthy",
                "endpoint": "ka-d0808962-endpoint",
                "client_initialized": self.knowledge_client is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "endpoint": "ka-d0808962-endpoint"
            }

def create_knowledge_assistant_tool_for_langchain(knowledge_client: KnowledgeAssistantMCPClient):
    """
    Create a LangChain tool wrapper for Knowledge Assistant
    
    Args:
        knowledge_client: Initialized KnowledgeAssistantMCPClient instance
        
    Returns:
        LangChain tool for Knowledge Assistant queries
    """
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
    
    class KnowledgeQueryInput(BaseModel):
        query: str = Field(description="Natural language query for knowledge analysis")
    
    class KnowledgeAssistantTool(BaseTool):
        name: str = "knowledge_assistant"
        description: str = """Use this tool to analyze unstructured text, documents, complaints, and knowledge base content. 
        This tool is specifically designed for:
        - Analyzing member complaints and feedback
        - Searching through policy documents and guidelines
        - Finding information in unstructured text data
        - Answering questions about billing codes, procedures, and policies
        - Analyzing communication logs and support tickets
        
        Use this when you need to search through documents, analyze text content, or find information that isn't in structured databases."""
        args_schema: type[BaseModel] = KnowledgeQueryInput
        
        def _run(self, query: str) -> str:
            """Execute Knowledge Assistant query"""
            result = knowledge_client.query_knowledge(query)
            
            if result["success"]:
                return f"Knowledge Analysis:\n{result['result']}"
            else:
                return f"Error querying Knowledge Assistant: {result['error']}"
    
    return KnowledgeAssistantTool()

def get_knowledge_assistant_mcp_client(workspace_client: WorkspaceClient) -> KnowledgeAssistantMCPClient:
    """Get initialized Knowledge Assistant MCP client"""
    return KnowledgeAssistantMCPClient(workspace_client)
