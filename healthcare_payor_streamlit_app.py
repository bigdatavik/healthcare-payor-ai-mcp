import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import json
from typing import Dict, List, Any
import traceback

# Databricks and LangChain imports
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import mlflow

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare Payor AI System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_member_id' not in st.session_state:
    st.session_state.current_member_id = None
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None

class HealthcarePayorAgent:
    """Healthcare Payor AI Agent using Databricks UC Tools and LangChain"""
    
    def __init__(self):
        # Get configuration from environment variables with defaults
        self.catalog = os.getenv('HEALTHCARE_CATALOG', 'my_catalog')
        self.schema = os.getenv('HEALTHCARE_SCHEMA', 'payer_silver')
        self.llm_endpoint = os.getenv('HEALTHCARE_LLM_ENDPOINT', 'databricks-meta-llama-3-3-70b-instruct')
        self.llm_temperature = float(os.getenv('HEALTHCARE_LLM_TEMPERATURE', '0.1'))
        self.debug = os.getenv('HEALTHCARE_DEBUG', 'false').lower() == 'true'
        
        self.client = None
        self.agent_executor = None
        self._setup_databricks_client()
        self._setup_uc_tools()
        self._setup_agent()
    
    def _setup_databricks_client(self):
        """Initialize Databricks client (works for both local and cloud)"""
        try:
            # For local development, use DEFAULT profile
            # For cloud deployment, use default authentication
            self.client = WorkspaceClient()
            st.success("✅ Connected to Databricks workspace")
        except Exception as e:
            st.error(f"❌ Failed to connect to Databricks: {e}")
            st.stop()
    
    def _setup_uc_tools(self):
        """Setup Unity Catalog tools for healthcare payor"""
        try:
            # Initialize UC Function Toolkit with our healthcare payor functions
            function_names = [
                f"{self.catalog}.{self.schema}.lookup_member",
                f"{self.catalog}.{self.schema}.lookup_claims", 
                f"{self.catalog}.{self.schema}.lookup_providers"
            ]
            
            self.toolkit = UCFunctionToolkit(function_names=function_names)
            self.tools = self.toolkit.tools
            
            st.success(f"✅ Loaded {len(self.tools)} UC tools")
            
        except Exception as e:
            st.error(f"❌ Failed to setup UC tools: {e}")
            st.error(f"Make sure UC functions are created in {self.catalog}.{self.schema}")
            st.stop()
    
    def _setup_agent(self):
        """Setup LangChain agent with UC tools"""
        try:
            # Initialize LLM
            self.llm = ChatDatabricks(
                endpoint=self.llm_endpoint, 
                temperature=self.llm_temperature
            )
            
            # Define the system prompt for healthcare payor
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a helpful Healthcare Payor AI Assistant. You help members, providers, and care managers with:
                
                - Member information lookup and benefits verification
                - Claims status and history inquiries  
                - Provider network searches and referrals
                - Healthcare coverage questions and guidance
                - Symptom assessment and general health advice
                
                Always use the available tools to get accurate, up-to-date information from the healthcare payor database.
                Be empathetic, professional, and provide clear explanations.
                
                Available tools:
                - lookup_member: Get member details, plan info, and enrollment status
                - lookup_claims: Retrieve member's claims history and status
                - lookup_providers: Search provider network by specialty
                
                Use these tools to provide accurate, personalized assistance."""),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Create agent with tools
            agent = create_tool_calling_agent(self.llm, self.tools, prompt)
            
            # Create agent executor with memory
            memory = ConversationBufferWindowMemory(
                k=10,
                memory_key="chat_history",
                return_messages=True
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                memory=memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            st.success("✅ Healthcare Payor AI Agent initialized")
            
        except Exception as e:
            st.error(f"❌ Failed to setup agent: {e}")
            st.stop()
    
    def chat(self, user_input: str) -> str:
        """Process user input and return AI response"""
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response["output"]
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🏥 Healthcare Payor AI System")
    st.markdown("**AI-Powered Healthcare Payor Assistant with Unity Catalog Integration**")
    
    # Initialize agent
    if st.session_state.agent_executor is None:
        with st.spinner("Initializing Healthcare Payor AI Agent..."):
            try:
                agent = HealthcarePayorAgent()
                st.session_state.agent_executor = agent.agent_executor
                st.session_state.agent = agent
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Member lookup
        st.subheader("Member Lookup")
        member_id = st.text_input("Enter Member ID", placeholder="e.g., M001")
        if st.button("🔍 Lookup Member") and member_id:
            with st.spinner("Looking up member..."):
                try:
                    # Use the agent to lookup member
                    response = st.session_state.agent.chat(f"Look up member {member_id}")
                    st.session_state.current_member_id = member_id
                    st.success(f"Found member: {member_id}")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Provider search
        st.subheader("Provider Search")
        specialty = st.text_input("Enter Specialty", placeholder="e.g., Cardiology")
        if st.button("🏥 Search Providers") and specialty:
            with st.spinner("Searching providers..."):
                try:
                    response = st.session_state.agent.chat(f"Find providers specializing in {specialty}")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.session_state.current_member_id = None
            st.rerun()
    
    # Main chat interface
    st.header("💬 Chat with Healthcare Payor AI")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about members, claims, providers, or health questions..."):
        # Add user message to history
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.chat(prompt)
                    st.write(response)
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.write(error_msg)
                    st.session_state.conversation_history.append({"role": "assistant", "content": error_msg})
    
    # Feature highlights
    st.markdown("---")
    st.header("🚀 Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("👤 Member Services")
        st.markdown("""
        - Member information lookup
        - Benefits verification
        - Claims status inquiries
        - Coverage questions
        """)
    
    with col2:
        st.subheader("🏥 Provider Relations")
        st.markdown("""
        - Provider network search
        - Specialty referrals
        - Network status checks
        - Provider directory
        """)
    
    with col3:
        st.subheader("🤖 AI-Powered")
        st.markdown("""
        - Natural language queries
        - Symptom assessment
        - Health guidance
        - Real-time data access
        """)
    
    # Technical info
    with st.expander("🔧 Technical Details"):
        st.markdown(f"""
        **Configuration:**
        - Catalog: `my_catalog`
        - Schema: `payer_silver`
        - LLM: `databricks-meta-llama-3-3-70b-instruct`
        - UC Tools: `lookup_member`, `lookup_claims`, `lookup_providers`
        
        **Integration:**
        - Databricks Unity Catalog functions
        - LangChain agent framework
        - Streamlit web interface
        """)

if __name__ == "__main__":
    main()
