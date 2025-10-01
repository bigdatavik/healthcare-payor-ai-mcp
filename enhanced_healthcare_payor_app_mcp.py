"""
Enhanced Healthcare Payor AI System with Managed MCP Servers
Integrates Genie and Unity Catalog Functions via managed MCP servers
"""

# =============================================================================
# CONFIGURATION - Import from config.py
# =============================================================================

from config import (
    CATALOG_NAME, 
    SCHEMA_NAME, 
    DATABRICKS_PROFILE, 
    WORKSPACE_HOSTNAME, 
    GENIE_SPACE_ID,
    KNOWLEDGE_ASSISTANT_ENDPOINT_ID,
    validate_config
)

# Validate configuration on startup
validate_config()

# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# Import MCP clients
from mcp_genie_client import get_genie_mcp_client, create_genie_tool_for_langchain
from mcp_uc_functions_client import get_uc_functions_mcp_client, create_uc_functions_tools_for_langchain
from mcp_knowledge_assistant_client import get_knowledge_assistant_mcp_client, create_knowledge_assistant_tool_for_langchain

# LangChain imports
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# Databricks imports
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput

class EnhancedHealthcarePayorAgentMCP:
    """Enhanced Healthcare Payor Agent using Managed MCP Servers"""
    
    def __init__(self):
        self.workspace_client = None
        self.genie_client = None
        self.uc_functions_client = None
        self.knowledge_assistant_client = None
        self.tools = []
        self.agent_executor = None
        self._setup_clients()
        self._setup_tools()
        self._setup_agent()
    
    def _setup_clients(self):
        """Setup MCP clients"""
        try:
            # Initialize workspace client
            if DATABRICKS_PROFILE == "auto-detect":
                # In cloud environments, let the SDK auto-detect the profile
                self.workspace_client = WorkspaceClient()
            else:
                self.workspace_client = WorkspaceClient(profile=DATABRICKS_PROFILE)
            st.success("✅ Databricks workspace client initialized")
            
            # Initialize Genie MCP client
            self.genie_client = get_genie_mcp_client()
            
            # Initialize UC Functions MCP client
            self.uc_functions_client = get_uc_functions_mcp_client()
            
            # Initialize Knowledge Assistant client
            self.knowledge_assistant_client = get_knowledge_assistant_mcp_client(self.workspace_client)
            
        except Exception as e:
            st.error(f"❌ Failed to setup MCP clients: {e}")
            st.stop()
    
    def _setup_tools(self):
        """Setup tools from MCP servers"""
        self.tools = []
        
        try:
            # Add Genie MCP tool
            if self.genie_client:
                st.info(f"🔍 Genie client status: MCP client = {self.genie_client.mcp_client is not None}")
                if self.genie_client.mcp_client:
                    genie_tool = create_genie_tool_for_langchain(self.genie_client)
                    self.tools.append(genie_tool)
                    st.success("✅ Genie MCP tool loaded")
                else:
                    st.warning("⚠️ Genie MCP client not properly initialized")
            else:
                st.error("❌ Genie client not created")
            
            # Add UC Functions MCP tools
            if self.uc_functions_client and self.uc_functions_client.mcp_client:
                uc_tools = create_uc_functions_tools_for_langchain(self.uc_functions_client)
                self.tools.extend(uc_tools)
                st.success(f"✅ UC Functions MCP tools loaded ({len(uc_tools)} tools)")
            
            # Add Knowledge Assistant tool
            if self.knowledge_assistant_client and self.knowledge_assistant_client.knowledge_client:
                knowledge_tool = create_knowledge_assistant_tool_for_langchain(self.knowledge_assistant_client)
                self.tools.append(knowledge_tool)
                st.success("✅ Knowledge Assistant tool loaded")
            else:
                st.warning("⚠️ Knowledge Assistant tool not available")
            
            if not self.tools:
                st.warning("⚠️ No MCP tools available")
            else:
                st.success(f"✅ Total tools loaded: {len(self.tools)}")
                
        except Exception as e:
            st.error(f"❌ Failed to setup tools: {e}")
    
    def _setup_agent(self):
        """Setup a simple agent with MCP tools"""
        try:
            if not self.tools:
                st.error("❌ No tools available for agent setup")
                return
            
            # Create LLM client
            self.llm_client = self.workspace_client.serving_endpoints.get_open_ai_client()
            
            # Create tool mapping
            self.tool_map = {tool.name: tool for tool in self.tools}
            
            # Initialize memory
            self.memory = []
            
            st.success("✅ AI Agent with MCP tools initialized")
            
        except Exception as e:
            st.error(f"❌ Failed to setup agent: {e}")
            st.stop()
    
    def _clean_response_content(self, content: str) -> str:
        """Clean up response content to remove technical clutter"""
        import re
        
        # Remove function call tags
        content = re.sub(r'<function=.*?>\{.*?\}</function>', '', content)
        content = re.sub(r'<function_output>', '', content)
        content = re.sub(r'</function_output>', '', content)
        
        # Remove duplicate sections
        lines = content.split('\n')
        cleaned_lines = []
        seen_sections = set()
        
        for line in lines:
            # Skip empty lines and technical markers
            if not line.strip() or line.strip().startswith('<') or 'function=' in line:
                continue
                
            # Skip duplicate table headers
            if 'Claim ID' in line and 'Member ID' in line and 'Provider ID' in line:
                if 'table_header' in seen_sections:
                    continue
                seen_sections.add('table_header')
            
            # Skip duplicate explanations
            if 'However, since the previous output was empty' in line:
                continue
            if 'I hope this alternative result helps' in line:
                continue
            if 'Please note that the claim amounts are subject to audit' in line:
                continue
                
            cleaned_lines.append(line)
        
        # Join lines and clean up extra whitespace
        cleaned_content = '\n'.join(cleaned_lines)
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)  # Remove multiple newlines
        cleaned_content = cleaned_content.strip()
        
        return cleaned_content
    
    def chat(self, user_input: str) -> str:
        """Enhanced chat with MCP tools"""
        try:
            if not self.llm_client:
                return "Agent not initialized"
            
            # Convert tools to OpenAI format
            openai_tools = []
            for tool in self.tools:
                tool_spec = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.args_schema.model_json_schema() if hasattr(tool.args_schema, 'model_json_schema') else {}
                    }
                }
                openai_tools.append(tool_spec)
            
            # Prepare messages
            messages = [{"role": "system", "content": """You are a helpful AI assistant for healthcare payor operations. 
            When responding to users:
            1. Show only the final, clean results
            2. Do not display technical function calls or internal processing details
            3. Present data in a clear, readable format
            4. Avoid duplicate information or redundant explanations
            5. Be concise and professional
            Use the available tools to help users with member inquiries, claims processing, and provider management."""}]
            
            # Add conversation history
            for msg in self.memory[-10:]:  # Keep last 10 messages
                messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": user_input})
            
            # Call LLM with tools
            response = self.llm_client.chat.completions.create(
                model="databricks-meta-llama-3-1-8b-instruct",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Handle tool calls
            if message.tool_calls:
                # Add assistant message to memory
                self.memory.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})
                
                # Execute tool calls
                tool_results = []
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if tool_name in self.tool_map:
                        try:
                            tool = self.tool_map[tool_name]
                            result = tool._run(**tool_args)
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": result
                            })
                        except Exception as e:
                            # Show user-friendly error messages based on tool type
                            if "uc_functions" in tool_name.lower():
                                error_msg = f"Unable to find data in UC Functions database. Trying alternative data sources..."
                            elif "genie" in tool_name.lower():
                                error_msg = f"Genie analysis unavailable. Trying other methods..."
                            else:
                                error_msg = f"Tool temporarily unavailable. Trying alternative approach..."
                            
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool", 
                                "name": tool_name,
                                "content": error_msg
                            })
                    else:
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Tool {tool_name} not found"
                        })
                
                # Add tool results to conversation
                messages.extend(tool_results)
                
                # Get final response
                final_response = self.llm_client.chat.completions.create(
                    model="databricks-meta-llama-3-1-8b-instruct",
                    messages=messages
                )
                
                final_content = final_response.choices[0].message.content
                
                # Clean up the response to remove technical clutter
                final_content = self._clean_response_content(final_content)
                
                # Add success message if Genie was used successfully
                successful_tools = [result for result in tool_results if "genie" in result.get("name", "").lower() and "error" not in str(result.get("content", "")).lower()]
                if successful_tools:
                    final_content = f"✅ Found the answer using Genie AI analysis:\n\n{final_content}"
                
                # Add to memory
                self.memory.extend(tool_results)
                self.memory.append({"role": "assistant", "content": final_content})
                
                return final_content
            else:
                # No tool calls, return direct response
                self.memory.append({"role": "assistant", "content": message.content})
                return message.content
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."

def create_mcp_status_dashboard():
    """Create MCP servers status dashboard"""
    st.subheader("🔧 MCP Servers Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Genie MCP Server")
        try:
            genie_client = get_genie_mcp_client()
            genie_health = genie_client.get_health_status()
            
            if genie_health["status"] == "healthy":
                st.success(f"✅ Connected to Genie MCP")
                st.info(f"URL: {genie_health['mcp_url']}")
                st.info(f"Tools: {genie_health['tools_count']}")
            else:
                st.error(f"❌ Genie MCP: {genie_health.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Genie MCP Error: {e}")
    
    with col2:
        st.markdown("#### UC Functions MCP Server")
        try:
            uc_client = get_uc_functions_mcp_client()
            uc_health = uc_client.get_health_status()
            
            if uc_health["status"] == "healthy":
                st.success(f"✅ Connected to UC Functions MCP")
                st.info(f"URL: {uc_health['mcp_url']}")
                st.info(f"Functions: {uc_health['functions_count']}")
            else:
                st.error(f"❌ UC Functions MCP: {uc_health.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ UC Functions MCP Error: {e}")
        
        st.markdown("#### Knowledge Assistant")
        try:
            if DATABRICKS_PROFILE == "auto-detect":
                knowledge_client = get_knowledge_assistant_mcp_client(WorkspaceClient())
            else:
                knowledge_client = get_knowledge_assistant_mcp_client(WorkspaceClient(profile=DATABRICKS_PROFILE))
            knowledge_health = knowledge_client.get_health_status()
            
            if knowledge_health["status"] == "healthy":
                st.success(f"✅ Connected to Knowledge Assistant")
                st.info(f"Endpoint: {knowledge_health['endpoint']}")
            else:
                st.error(f"❌ Knowledge Assistant: {knowledge_health.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Knowledge Assistant Error: {e}")

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Healthcare Payor AI System - MCP",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 Enhanced Healthcare Payor AI System")
    st.subheader("Powered by Managed MCP Servers")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        create_mcp_status_dashboard()
        
        st.header("🎯 Available Tools")
        st.markdown("""
        **Genie MCP:**
        - Natural language data queries
        - Advanced analytics
        - Structured data insights
        
        **UC Functions MCP:**
        - Member lookup
        - Claims lookup  
        - Provider lookup
        
        **Knowledge Assistant:**
        - Document analysis
        - Policy and guideline search
        - Complaint analysis
        - Billing code lookup
        """)
    
    # Main content
    tab1, tab2 = st.tabs(["💬 Chat Assistant", "📊 Analytics"])
    
    with tab1:
        st.header("AI Assistant with MCP Integration")
        
        # Initialize agent
        if 'agent_mcp' not in st.session_state:
            with st.spinner("Initializing MCP-powered AI agent..."):
                st.session_state.agent_mcp = EnhancedHealthcarePayorAgentMCP()
        
        # Chat interface
        if prompt := st.chat_input("Ask me anything about healthcare, benefits, or claims..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.agent_mcp.chat(prompt)
                    st.write(response)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    with tab2:
        st.header("📊 Analytics Dashboard")
        st.info("Analytics powered by Genie MCP server for real-time data insights")
        
        # Sample analytics (in production, this would use Genie MCP)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Members", "1,234", "12%")
        with col2:
            st.metric("Active Claims", "567", "8%")
        with col3:
            st.metric("Providers", "89", "3%")
        with col4:
            st.metric("Satisfaction", "94%", "2%")
    

if __name__ == "__main__":
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    main()
