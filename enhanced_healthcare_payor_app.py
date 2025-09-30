import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import os
import json
from typing import Dict, List, Any, Optional
import traceback
import hashlib
import time

# Databricks and LangChain imports
from databricks.sdk import WorkspaceClient
from databricks_langchain import ChatDatabricks, UCFunctionToolkit
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import mlflow

# Enhanced features imports
from genie_multiagent_tool import create_genie_tool

# Knowledge Assistant imports
from openai import OpenAI

# Configure Streamlit page
st.set_page_config(
    page_title="Healthcare Payor AI System - Enhanced",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.databricks.com',
        'Report a bug': "https://github.com/databricks",
        'About': "Healthcare Payor AI System v2.0"
    }
)

# Custom CSS for modern healthcare UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3c72;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active { background-color: #28a745; }
    .status-pending { background-color: #ffc107; }
    .status-denied { background-color: #dc3545; }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
    }
    .ai-message {
        background-color: #f5f5f5;
        margin-right: auto;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced features
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_member_id' not in st.session_state:
    st.session_state.current_member_id = None
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'member'  # member, provider, care_manager, admin
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = {}
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = []
if 'workflow_status' not in st.session_state:
    st.session_state.workflow_status = {}

class EnhancedHealthcarePayorAgent:
    """Enhanced Healthcare Payor AI Agent with industry best practices"""
    
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
        """Initialize Databricks client with enhanced error handling"""
        try:
            self.client = WorkspaceClient()
            st.success("✅ Connected to Databricks workspace")
            self._log_audit_event("system", "databricks_connection", "success")
        except Exception as e:
            st.error(f"❌ Failed to connect to Databricks: {e}")
            self._log_audit_event("system", "databricks_connection", "failed", str(e))
            st.stop()
    
    def _setup_uc_tools(self):
        """Setup Unity Catalog tools with fallback for missing functions"""
        try:
            # Start with basic UC functions that should exist
            basic_function_names = [
                f"{self.catalog}.{self.schema}.lookup_member",
                f"{self.catalog}.{self.schema}.lookup_claims", 
                f"{self.catalog}.{self.schema}.lookup_providers"
            ]
            
            # Try to load basic functions first
            self.toolkit = UCFunctionToolkit(function_names=basic_function_names)
            self.tools = self.toolkit.tools
            
            st.success(f"✅ Loaded {len(self.tools)} basic UC tools")
            self._log_audit_event("system", "uc_tools_loaded", "success", f"Basic tools: {len(self.tools)}")
            
            # Try to add enhanced functions if they exist
            enhanced_function_names = [
                f"{self.catalog}.{self.schema}.check_eligibility",
                f"{self.catalog}.{self.schema}.get_benefits",
                f"{self.catalog}.{self.schema}.search_network",
                f"{self.catalog}.{self.schema}.get_authorization_status",
                f"{self.catalog}.{self.schema}.submit_prior_auth"
            ]
            
            try:
                enhanced_toolkit = UCFunctionToolkit(function_names=enhanced_function_names)
                self.tools.extend(enhanced_toolkit.tools)
                st.success(f"✅ Loaded {len(enhanced_toolkit.tools)} enhanced UC tools")
                self._log_audit_event("system", "enhanced_uc_tools_loaded", "success", f"Enhanced tools: {len(enhanced_toolkit.tools)}")
            except Exception as enhanced_error:
                st.warning(f"⚠️ Enhanced UC functions not available: {enhanced_error}")
                st.info("💡 Using basic UC functions with enhanced UI features")
                self._log_audit_event("system", "enhanced_uc_tools_loaded", "partial", str(enhanced_error))
            
            # Enhanced tools loaded
            
            # Add Knowledge Assistant tool for unstructured text analysis
            try:
                knowledge_tool = self._create_knowledge_assistant_tool()
                if knowledge_tool:
                    self.tools.append(knowledge_tool)
                    st.success("✅ Loaded Knowledge Assistant tool")
                    self._log_audit_event("system", "knowledge_tool_loaded", "success")
                else:
                    st.warning("⚠️ Knowledge Assistant tool not available")
                    self._log_audit_event("system", "knowledge_tool_loaded", "warning", "Tool creation failed")
            except Exception as e:
                st.warning(f"⚠️ Knowledge Assistant tool not available: {e}")
                self._log_audit_event("system", "knowledge_tool_loaded", "warning", str(e))
            
        except Exception as e:
            st.error(f"❌ Failed to setup basic UC tools: {e}")
            st.error(f"Make sure basic UC functions are created in {self.catalog}.{self.schema}")
            st.info("💡 You can still use the enhanced UI features without UC functions")
            self._log_audit_event("system", "uc_tools_loaded", "failed", str(e))
            
            # Create empty tools list to prevent app crash
            self.tools = []
        
        # Add Genie tool for natural language data queries
        try:
            genie_tool = create_genie_tool()
            self.tools.append(genie_tool)
            st.success(f"✅ Added Genie tool for natural language data queries")
            self._log_audit_event("system", "genie_tool_loaded", "success", "Genie tool added")
        except Exception as genie_error:
            st.warning(f"⚠️ Genie tool not available: {genie_error}")
            st.info("💡 Running without Genie tool - data analysis features may be limited")
    
    def _create_knowledge_assistant_tool(self):
        """Create Knowledge Assistant tool for unstructured text analysis"""
        from langchain.tools import BaseTool
        
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
            
            def __init__(self, databricks_client):
                super().__init__()
                self._databricks_client = databricks_client
                self._knowledge_client = None
                self._setup_knowledge_client()
            
            def _setup_knowledge_client(self):
                """Setup the Knowledge Assistant client using token generation"""
                try:
                    # Generate a token using the Databricks client
                    import time
                    token = self._databricks_client.tokens.create(
                        comment=f"knowledge-assistant-{time.time_ns()}", 
                        lifetime_seconds=3600
                    )
                    
                    # Initialize OpenAI client for Knowledge Assistant
                    self._knowledge_client = OpenAI(
                        api_key=token.token_value,
                        base_url="https://adb-984752964297111.11.azuredatabricks.net/serving-endpoints"
                    )
                    
                    # Store token info for cleanup
                    self._token_info = token.token_info
                    print("✅ Knowledge Assistant client setup with token generation")
                except Exception as e:
                    st.warning(f"⚠️ Failed to setup Knowledge Assistant client: {e}")
                    self._knowledge_client = None
            
            def _run(self, query: str) -> str:
                """Execute the Knowledge Assistant query"""
                if not self._knowledge_client:
                    return "❌ Knowledge Assistant not available - client not initialized"
                
                try:
                    # Use the OpenAI client to query the Knowledge Assistant
                    response = self._knowledge_client.responses.create(
                        model="ka-d0808962-endpoint",
                        input=[
                            {
                                "role": "user",
                                "content": query
                            }
                        ]
                    )
                    
                    if response.output and len(response.output) > 0:
                        return response.output[0].content[0].text
                    else:
                        return "❌ No response from Knowledge Assistant"
                        
                except Exception as e:
                    return f"❌ Knowledge Assistant error: {str(e)}"
            
            async def _arun(self, query: str) -> str:
                """Async version of the tool"""
                return self._run(query)
        
        return KnowledgeAssistantTool(self.client)
    
    def _setup_agent(self):
        """Setup enhanced LangChain agent with role-based prompts"""
        try:
            # Initialize LLM
            self.llm = ChatDatabricks(
                endpoint=self.llm_endpoint, 
                temperature=self.llm_temperature
            )
            
            # Role-based system prompts
            role_prompts = {
                'member': """You are a helpful Healthcare Payor AI Assistant for members. You help with:
                - Member information lookup and benefits verification
                - Claims status and history inquiries  
                - Provider network searches and referrals
                - Healthcare coverage questions and guidance
                - Prior authorization status
                - Copay and deductible information
                - Finding in-network providers
                
                Always be empathetic, clear, and provide actionable next steps.""",
                
                'provider': """You are a Healthcare Payor AI Assistant for healthcare providers. You help with:
                - Patient eligibility verification
                - Benefits and coverage details
                - Prior authorization requirements
                - Claims submission guidance
                - Network status verification
                - Reimbursement information
                - Quality metrics and reporting
                
                Provide detailed, clinical-grade information for healthcare decisions.""",
                
                'care_manager': """You are a Healthcare Payor AI Assistant for care managers. You help with:
                - Member risk stratification
                - Care gap analysis
                - Intervention opportunities
                - Quality measure tracking
                - Member engagement strategies
                - Provider performance metrics
                - Population health insights
                
                Focus on data-driven care management and quality improvement.""",
                
                'admin': """You are a Healthcare Payor AI Assistant for administrators. You help with:
                - System analytics and reporting
                - Performance metrics
                - Cost analysis
                - Compliance monitoring
                - Workflow optimization
                - Risk management
                - Strategic planning support
                
                Provide comprehensive administrative insights and recommendations."""
            }
            
            # Get current user role
            user_role = st.session_state.get('user_role', 'member')
            system_prompt = role_prompts.get(user_role, role_prompts['member'])
            
            # Enhanced prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""{system_prompt}
                
Available Tools:
- UC Functions: For member lookup, claims lookup, provider lookup, and business logic queries
- Genie Tool: For natural language data analysis queries (e.g., "What are the different statuses of claims?", "Show me the top 5 claims by amount", "What is the average claim amount by provider?")

Tool Selection Guidelines:
- Use UC Functions for specific entity lookups (member ID, claim ID, provider ID)
- Use Genie Tool for data analysis, aggregations, and exploratory queries
- Always use the most appropriate tool for the user's question

Always use the available tools to get accurate, up-to-date information from the healthcare payor database. Be professional, empathetic, and provide clear explanations with actionable next steps."""),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ])
            
            # Debug: Print tools being loaded
            print(f"DEBUG: Loading {len(self.tools)} tools:")
            for i, tool in enumerate(self.tools):
                print(f"  Tool {i+1}: {tool.name} - {tool.description[:50]}...")
            
            # Create agent with tools (handle empty tools case)
            if self.tools:
                agent = create_tool_calling_agent(self.llm, self.tools, prompt)
                print(f"DEBUG: Created tool-calling agent with {len(self.tools)} tools")
            else:
                # Create a simple agent without tools if UC functions are not available
                from langchain.agents import create_react_agent
                agent = create_react_agent(self.llm, [], prompt)
                print("DEBUG: Created simple agent without tools")
            
            # Enhanced memory with conversation context
            memory = ConversationBufferWindowMemory(
                k=15,  # Increased context window
                memory_key="chat_history",
                return_messages=True
            )
            
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools if self.tools else [], 
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,  # Prevent infinite loops
                early_stopping_method="generate"
            )
            
            st.success("✅ Enhanced Healthcare Payor AI Agent initialized")
            self._log_audit_event("system", "agent_initialized", "success", f"Role: {user_role}")
            
        except Exception as e:
            st.error(f"❌ Failed to setup agent: {e}")
            self._log_audit_event("system", "agent_initialized", "failed", str(e))
            st.stop()
    
    def _log_audit_event(self, user_type: str, action: str, status: str, details: str = ""):
        """Log audit events for compliance"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'user_type': user_type,
            'action': action,
            'status': status,
            'details': details,
            'session_id': st.session_state.get('session_id', 'unknown')
        }
        st.session_state.audit_log.append(event)
    
    def chat(self, user_input: str) -> str:
        """Enhanced chat with audit logging"""
        try:
            # Log the interaction
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "started",
                f"Input length: {len(user_input)}"
            )
            
            response = self.agent_executor.invoke({"input": user_input})
            
            # Log successful response
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "completed",
                f"Response length: {len(response['output'])}"
            )
            
            return response["output"]
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "error",
                str(e)
            )
            return error_msg
    
    def chat_with_tool_info(self, user_input: str) -> tuple[str, str]:
        """Enhanced chat with tool usage information for demo purposes"""
        try:
            # Log the interaction
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "started",
                f"Input length: {len(user_input)}"
            )
            
            # Get response with tool usage info
            print(f"DEBUG: Invoking agent with input: '{user_input}'")
            response = self.agent_executor.invoke({"input": user_input})
            
            # Extract tool usage information
            tool_used = "Unknown"
            
            # Debug: Print response structure to understand what we're getting
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict) and 'intermediate_steps' in response:
                print(f"DEBUG: Intermediate steps: {response['intermediate_steps']}")
                print(f"DEBUG: Number of intermediate steps: {len(response['intermediate_steps'])}")
            else:
                print("DEBUG: No intermediate_steps found in response")
            
            # Check for intermediate steps first (most reliable)
            if isinstance(response, dict) and response.get('intermediate_steps'):
                # Get the last tool used from intermediate steps
                last_step = response['intermediate_steps'][-1]
                if len(last_step) >= 2:
                    tool_name = last_step[0].tool
                    # Map tool names to display names
                    if 'knowledge_assistant' in tool_name:
                        tool_used = "Knowledge Assistant"
                    elif 'genie' in tool_name:
                        tool_used = "Genie Query"
                    elif any(uc_tool in tool_name for uc_tool in ['lookup_member', 'lookup_claims', 'lookup_providers']):
                        tool_used = "UC Functions"
                    else:
                        tool_used = tool_name
                    print(f"DEBUG: Detected tool from intermediate_steps: {tool_used}")
            # Check for Knowledge Assistant patterns in the output
            elif any(pattern in response.get('output', '').lower() for pattern in [
                'complained about', 'complaint', 'billing code', 'customer service', 
                'member called', 'agent:', 'member:', 'resolution', 'resolved by',
                'customer_service_communications', 'prior_authorization'
            ]) or any(pattern in response.get('output', '') for pattern in [
                '[^', ']', 'customer_service_communications.txt', 'prior_authorization_documents.txt'
            ]):
                tool_used = "Knowledge Assistant"
                print(f"DEBUG: Detected Knowledge Assistant from output patterns")
            # Check for Genie-specific patterns in the output
            elif any(pattern in response.get('output', '').lower() for pattern in [
                'genie analysis', 'sql query:', 'data (', 'status count', 
                'top 5', 'distribution', 'aggregate', 'group by', 'genie'
            ]):
                tool_used = "genie_query"
                print(f"DEBUG: Detected Genie tool from output patterns")
            # Check for UC function patterns - look for specific member/claim/provider data patterns
            elif any(pattern in response.get('output', '').lower() for pattern in [
                'member id:', 'first name:', 'last name:', 'birth date:', 'gender:', 'plan id:',
                'claim id:', 'total charge:', 'claim date:', 'claim status:',
                'provider id:', 'provider name:', 'specialty:', 'location:'
            ]):
                tool_used = "UC Functions"
                print(f"DEBUG: Detected UC Functions from output patterns")
            # Check for specific tool names in the output
            elif any(tool_name in response.get('output', '') for tool_name in [
                'lookup_member', 'lookup_claims', 'lookup_providers'
            ]):
                tool_used = "UC Functions"
                print(f"DEBUG: Detected UC Functions from tool names")
            else:
                tool_used = "Direct LLM Response"
                print(f"DEBUG: No tool patterns detected, using Direct LLM Response")
            
            # Add tool usage info to response
            enhanced_response = f"""🔧 **Tool Used:** {tool_used}

{response['output']}"""
            
            # Log successful response
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "completed",
                f"Response length: {len(response['output'])}, Tool: {tool_used}"
            )
            
            return enhanced_response, tool_used
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
            self._log_audit_event(
                st.session_state.get('user_role', 'member'),
                "chat_interaction",
                "error",
                str(e)
            )
            return error_msg, "Error"

def create_analytics_dashboard():
    """Create comprehensive analytics dashboard"""
    st.subheader("📊 Analytics Dashboard")
    
    # Sample analytics data (in production, this would come from your data warehouse)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Members",
            value="12,847",
            delta="+234 this month"
        )
    
    with col2:
        st.metric(
            label="Claims Processed",
            value="8,432",
            delta="+156 this week"
        )
    
    with col3:
        st.metric(
            label="Provider Network",
            value="2,156",
            delta="+23 new providers"
        )
    
    with col4:
        st.metric(
            label="Satisfaction Score",
            value="4.7/5.0",
            delta="+0.2 improvement"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Claims trend chart
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        claims_data = pd.DataFrame({
            'Month': dates,
            'Claims': [1200, 1350, 1180, 1420, 1380, 1550, 1620, 1480, 1390, 1510, 1680, 1750]
        })
        
        fig = px.line(claims_data, x='Month', y='Claims', title='Monthly Claims Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Member satisfaction by category
        satisfaction_data = pd.DataFrame({
            'Category': ['Claims Processing', 'Provider Network', 'Customer Service', 'Digital Experience'],
            'Score': [4.5, 4.8, 4.6, 4.3]
        })
        
        fig = px.bar(satisfaction_data, x='Category', y='Score', title='Satisfaction by Category')
        st.plotly_chart(fig, use_container_width=True)

def create_workflow_automation():
    """Create workflow automation interface"""
    st.subheader("🔄 Workflow Automation")
    
    # Workflow status
    workflow_tabs = st.tabs(["Prior Authorization", "Claims Processing", "Member Onboarding", "Provider Credentialing"])
    
    with workflow_tabs[0]:
        st.write("**Prior Authorization Workflow**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Select Member", ["M001 - John Doe", "M002 - Jane Smith", "M003 - Bob Johnson"])
            st.selectbox("Procedure", ["MRI Scan", "Surgery", "Specialist Visit"])
            st.date_input("Requested Date", value=date.today())
        
        with col2:
            st.write("**Status:**")
            st.markdown('<div class="status-indicator status-pending"></div>Pending Review', unsafe_allow_html=True)
            st.progress(0.6)
            st.write("**Next Steps:**")
            st.write("1. Clinical review in progress")
            st.write("2. Provider verification")
            st.write("3. Coverage determination")
        
        if st.button("Submit Prior Auth Request"):
            st.success("✅ Prior authorization request submitted successfully!")
    
    with workflow_tabs[1]:
        st.write("**Claims Processing Workflow**")
        
        # Claims processing metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pending Claims", "1,234", "↑ 12%")
        with col2:
            st.metric("Processed Today", "456", "↑ 8%")
        with col3:
            st.metric("Average Processing Time", "2.3 days", "↓ 0.5 days")
        
        # Claims processing queue
        st.write("**Processing Queue:**")
        claims_data = pd.DataFrame({
            'Claim ID': ['C001', 'C002', 'C003', 'C004'],
            'Member': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
            'Amount': ['$1,250', '$850', '$2,100', '$675'],
            'Status': ['Pending', 'Under Review', 'Approved', 'Pending'],
            'Days in Queue': [1, 3, 0, 2]
        })
        st.dataframe(claims_data, use_container_width=True)

def create_compliance_monitoring():
    """Create compliance monitoring interface"""
    st.subheader("🛡️ Compliance & Security Monitoring")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Security Alerts**")
        alert_data = [
            {"type": "info", "message": "All systems operational", "time": "2 min ago"},
            {"type": "warning", "message": "Unusual login pattern detected", "time": "15 min ago"},
            {"type": "success", "message": "Data backup completed", "time": "1 hour ago"}
        ]
        
        for alert in alert_data:
            alert_class = f"alert-{alert['type']}"
            st.markdown(f"""
            <div class="alert-box {alert_class}">
                <strong>{alert['message']}</strong><br>
                <small>{alert['time']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.write("**Compliance Status**")
        compliance_items = [
            {"item": "HIPAA Compliance", "status": "✅ Compliant", "last_check": "Today"},
            {"item": "SOC 2 Type II", "status": "✅ Compliant", "last_check": "Last week"},
            {"item": "Data Encryption", "status": "✅ Active", "last_check": "Ongoing"},
            {"item": "Access Controls", "status": "✅ Enforced", "last_check": "Real-time"}
        ]
        
        for item in compliance_items:
            st.write(f"**{item['item']}:** {item['status']}")
            st.caption(f"Last checked: {item['last_check']}")

def _display_structured_table(response: str):
    """Display structured data as a proper Streamlit table"""
    
    # Extract the data from the response
    if "Status Count" in response:
        # Parse the data from the response
        data_section = response.split("Status Count")[1].split("Summary:")[0].strip()
        
        # Parse the data into rows
        rows = []
        parts = data_section.split()
        
        # Group by pairs (status, value)
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                status = parts[i]
                value = parts[i + 1]
                try:
                    # Try to convert to float for numeric values
                    numeric_value = float(value)
                    rows.append([status, numeric_value])
                except ValueError:
                    # Keep as string if not numeric
                    rows.append([status, value])
        
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=['Status', 'Count'])
            
            # Display as a proper Streamlit table
            st.subheader("📊 Results Table")
            st.dataframe(df, use_container_width=True)
            
            # Show summary
            st.success(f"✅ Found {len(df)} records")
            
            # Show the rest of the response
            st.markdown("---")
            st.markdown("**Additional Information:**")
            st.markdown(response.split("Summary:")[1] if "Summary:" in response else "")
    
    else:
        # Fallback to regular markdown
        st.markdown(response)

def _display_formatted_response(response: str):
    """Display the multi-agent response with better formatting"""
    
    st.info(f"🔍 Debug: _display_formatted_response called with response length: {len(response)}")
    
    # Check if this is the old format with inline data
    if "Data (" in response and "• Row" in response:
        st.info("🔍 Debug: Detected old format with inline data")
        # Handle the old format where data is inline
        st.info("🔄 Converting old format to new display...")
        
        # Extract data from the inline format - handle both single line and multi-line
        data_rows = []
        
        # First try to find data in the response
        if "• Row" in response:
            # Split by "• Row" to get individual rows
            parts = response.split("• Row")
            for part in parts[1:]:  # Skip the first part (before first row)
                if ":" in part:
                    try:
                        # Extract the data part after the colon
                        data_part = part.split(":", 1)[1].strip()
                        # Clean up any trailing text
                        if "[" in data_part and "]" in data_part:
                            # Find the first [ and last ]
                            start = data_part.find("[")
                            end = data_part.rfind("]") + 1
                            data_part = data_part[start:end]
                            
                            import ast
                            row_data = ast.literal_eval(data_part)
                            data_rows.append(row_data)
                    except Exception as e:
                        st.warning(f"Could not parse row: {part[:50]}...")
                        continue
        
        # Display the data as a table
        if data_rows:
            st.subheader("📊 Results Table")
            import pandas as pd
            
            # Create DataFrame
            df = pd.DataFrame(data_rows)
            
            # Add column names
            if len(df.columns) >= 2:
                df.columns = ['Status', 'Count']
            
            # Display the table
            st.dataframe(df, use_container_width=True)
            
            # Show summary
            st.success(f"✅ Found {len(df)} records")
            
            # Also show the SQL query if present
            if "SELECT" in response:
                sql_start = response.find("SELECT")
                sql_end = response.find("```", sql_start)
                if sql_end == -1:
                    sql_end = response.find("\n", sql_start + 100)
                if sql_end > sql_start:
                    sql_query = response[sql_start:sql_end].strip()
                    st.subheader("🔍 SQL Query")
                    st.code(sql_query, language="sql")
            
            return
    
    # Handle the new format
    lines = response.split('\n')
    current_section = None
    sql_query = None
    data_rows = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle different sections
        if line.startswith("## 🔮 Genie Analysis"):
            st.markdown(line)
        elif line.startswith("**Query:**"):
            st.markdown(line)
        elif line.startswith("**Status:**"):
            st.markdown(line)
        elif line.startswith("### 📊 Result"):
            st.markdown(line)
        elif line.startswith("**SQL Query:**"):
            st.markdown(line)
        elif line.startswith("```sql"):
            # SQL query starts
            current_section = "sql"
            sql_query = []
        elif line.startswith("```") and current_section == "sql":
            # SQL query ends
            if sql_query:
                st.code('\n'.join(sql_query), language="sql")
            current_section = None
            sql_query = None
        elif current_section == "sql":
            sql_query.append(line)
        elif line.startswith("**Description:**"):
            st.markdown(line)
        elif line.startswith("**Data ("):
            st.markdown(line)
            current_section = "data"
        elif line.startswith("• Row") and current_section == "data":
            # Parse data row
            try:
                # Extract the data part after the colon
                data_part = line.split(":", 1)[1].strip()
                if data_part.startswith("[") and data_part.endswith("]"):
                    import ast
                    row_data = ast.literal_eval(data_part)
                    data_rows.append(row_data)
            except:
                continue
        elif line.startswith("**Error:**"):
            st.error(line)
        elif current_section == "data" and line.startswith("•"):
            # More data rows
            try:
                data_part = line.split(":", 1)[1].strip()
                if data_part.startswith("[") and data_part.endswith("]"):
                    import ast
                    row_data = ast.literal_eval(data_part)
                    data_rows.append(row_data)
            except:
                continue
        else:
            # Regular text
            if line and not line.startswith("**"):
                st.markdown(line)
    
    # Display data as a table if we have data rows
    if data_rows:
        st.subheader("📊 Results Table")
        import pandas as pd
        
        # Create DataFrame
        df = pd.DataFrame(data_rows)
        
        # Add column names if we can infer them
        if len(df.columns) >= 2:
            df.columns = ['Status', 'Count'] if 'claim_status' in str(response) else df.columns
        
        # Display the table
        st.dataframe(df, use_container_width=True)
        
        # Also show summary
        if len(df) > 0:
            st.success(f"✅ Found {len(df)} records")


def main():
    """Enhanced main Streamlit application"""
    
    # Enhanced header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Healthcare Payor AI System - Enhanced</h1>
        <p>AI-Powered Healthcare Payor Assistant with Advanced Analytics & Workflow Automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role selection
    st.sidebar.header("👤 User Role")
    user_role = st.sidebar.selectbox(
        "Select your role:",
        ["member", "provider", "care_manager", "admin"],
        index=["member", "provider", "care_manager", "admin"].index(st.session_state.get('user_role', 'member'))
    )
    st.session_state.user_role = user_role
    
    # Initialize agent with role-based configuration
    if st.session_state.agent_executor is None:
        with st.spinner("Initializing Enhanced Healthcare Payor AI Agent..."):
            try:
                agent = EnhancedHealthcarePayorAgent()
                st.session_state.agent_executor = agent.agent_executor
                st.session_state.agent = agent
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()
    
    # Main interface tabs
    main_tabs = st.tabs(["💬 AI Assistant", "📊 Analytics", "🔄 Workflows", "🛡️ Compliance", "📋 Reports"])
    
    # AI Assistant Tab
    with main_tabs[0]:
        st.header("🤖 AI Assistant")
        
        # Quick actions based on role
        if user_role == "member":
            st.write("**Quick Actions for Members:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Check Benefits"):
                    st.session_state.quick_action = "check_benefits"
            with col2:
                if st.button("🏥 Find Providers"):
                    st.session_state.quick_action = "find_providers"
            with col3:
                if st.button("📋 Claims Status"):
                    st.session_state.quick_action = "claims_status"
        
        elif user_role == "provider":
            st.write("**Quick Actions for Providers:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👤 Verify Eligibility"):
                    st.session_state.quick_action = "verify_eligibility"
            with col2:
                if st.button("📝 Submit Prior Auth"):
                    st.session_state.quick_action = "submit_prior_auth"
            with col3:
                if st.button("💰 Check Reimbursement"):
                    st.session_state.quick_action = "check_reimbursement"
        
        # Chat interface
        st.write("**Chat with AI Assistant:**")
        
        # Display conversation history
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show tool information if available
                tool_info = ""
                if "tool_used" in message:
                    tool_info = f"<br><small>🔧 <strong>Tool Used:</strong> {message['tool_used']}</small>"
                
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>AI Assistant:</strong> {message["content"]}{tool_info}
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input with form to handle clearing
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask me anything about healthcare, benefits, or claims:", key="chat_input")
            submitted = st.form_submit_button("Send")
            
            if submitted and user_input:
                with st.spinner("AI is thinking..."):
                    # Get the response and tool usage info
                    response, tool_used = st.session_state.agent.chat_with_tool_info(user_input)
                    
                    # Add to conversation history with tool info
                    st.session_state.conversation_history.append({"role": "user", "content": user_input})
                    st.session_state.conversation_history.append({
                        "role": "assistant", 
                        "content": response,
                        "tool_used": tool_used
                    })
                    
                    st.rerun()
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()
    
    
    # Analytics Tab
    with main_tabs[1]:
        create_analytics_dashboard()
    
    # Workflows Tab
    with main_tabs[2]:
        create_workflow_automation()
    
    # Compliance Tab
    with main_tabs[3]:
        create_compliance_monitoring()
    
    # Reports Tab
    with main_tabs[4]:
        st.subheader("📋 Reports & Documentation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Available Reports:**")
            report_options = [
                "Member Demographics Report",
                "Claims Analysis Report", 
                "Provider Performance Report",
                "Cost Analysis Report",
                "Quality Metrics Report",
                "Compliance Audit Report"
            ]
            
            selected_report = st.selectbox("Select Report:", report_options)
            if st.button("Generate Report"):
                st.success(f"✅ {selected_report} generated successfully!")
        
        with col2:
            st.write("**Audit Log:**")
            if st.session_state.audit_log:
                # Show recent audit events
                recent_events = st.session_state.audit_log[-10:]  # Last 10 events
                for event in reversed(recent_events):
                    st.write(f"**{event['timestamp']}** - {event['action']} ({event['status']})")
            else:
                st.write("No audit events recorded yet.")

if __name__ == "__main__":
    main()
