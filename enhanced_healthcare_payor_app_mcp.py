"""
Enhanced Healthcare Payor AI System with Managed MCP Servers
Integrates Genie and Unity Catalog Functions via managed MCP servers
"""

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
        self.tools = []
        self.agent_executor = None
        self._setup_clients()
        self._setup_tools()
        self._setup_agent()
    
    def _setup_clients(self):
        """Setup MCP clients"""
        try:
            # Initialize workspace client
            self.workspace_client = WorkspaceClient(profile="DEFAULT_azure")
            st.success("✅ Databricks workspace client initialized")
            
            # Initialize Genie MCP client
            self.genie_client = get_genie_mcp_client()
            
            # Initialize UC Functions MCP client
            self.uc_functions_client = get_uc_functions_mcp_client()
            
        except Exception as e:
            st.error(f"❌ Failed to setup MCP clients: {e}")
            st.stop()
    
    def _setup_tools(self):
        """Setup tools from MCP servers"""
        self.tools = []
        
        try:
            # Add Genie MCP tool
            if self.genie_client and self.genie_client.mcp_client:
                genie_tool = create_genie_tool_for_langchain(self.genie_client)
                self.tools.append(genie_tool)
                st.success("✅ Genie MCP tool loaded")
            
            # Add UC Functions MCP tools
            if self.uc_functions_client and self.uc_functions_client.mcp_client:
                uc_tools = create_uc_functions_tools_for_langchain(self.uc_functions_client)
                self.tools.extend(uc_tools)
                st.success(f"✅ UC Functions MCP tools loaded ({len(uc_tools)} tools)")
            
            if not self.tools:
                st.warning("⚠️ No MCP tools available")
            else:
                st.success(f"✅ Total tools loaded: {len(self.tools)}")
                
        except Exception as e:
            st.error(f"❌ Failed to setup tools: {e}")
    
    def _setup_agent(self):
        """Setup the LangChain agent with MCP tools"""
        try:
            if not self.tools:
                st.error("❌ No tools available for agent setup")
                return
            
            # Create LLM client
            llm = self.workspace_client.serving_endpoints.get_open_ai_client()
            
            # Define system prompt
            system_prompt = """You are an AI assistant for a healthcare payor organization. 
            You help with member inquiries, claims processing, and provider management.
            
            Available tools:
            - Genie MCP: Query structured data using natural language for data analysis
            - UC Functions: Lookup member information, claims, and providers from Unity Catalog
            
            Always use the appropriate tool for the user's request and provide helpful, accurate responses."""
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad")
            ])
            
            # Create memory
            memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=10
            )
            
            # Create agent
            agent = create_tool_calling_agent(llm, self.tools, prompt)
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            st.success("✅ AI Agent with MCP tools initialized")
            
        except Exception as e:
            st.error(f"❌ Failed to setup agent: {e}")
            st.stop()
    
    def chat(self, user_input: str) -> str:
        """Enhanced chat with MCP tools"""
        try:
            if not self.agent_executor:
                return "Agent not initialized"
            
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
            
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
        """)
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["💬 Chat Assistant", "📊 Analytics", "🔧 MCP Tools"])
    
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
    
    with tab3:
        st.header("🔧 MCP Tools Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Genie MCP Test")
            genie_query = st.text_input("Enter Genie query:", "What tables are available?")
            if st.button("Test Genie MCP"):
                try:
                    genie_client = get_genie_mcp_client()
                    result = genie_client.query_genie(genie_query)
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            st.subheader("UC Functions MCP Test")
            member_id = st.text_input("Enter Member ID:", "1001")
            if st.button("Test UC Functions MCP"):
                try:
                    uc_client = get_uc_functions_mcp_client()
                    result = uc_client.lookup_member(member_id)
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    main()
