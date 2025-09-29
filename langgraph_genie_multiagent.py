#!/usr/bin/env python3
"""
LangGraph Multi-Agent System with Genie Integration
This module implements a multi-agent workflow using LangGraph for healthcare payor system.
"""

import os
import json
from typing import Dict, List, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass

# LangChain imports
try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    from langchain.tools import BaseTool
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available, using fallback")

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️ LangGraph not available, using fallback")

# Local imports
from genie_multiagent_tool import create_genie_tool

# Try to import UC tools
try:
    from databricks_langchain import UCFunctionToolkit
    UC_TOOLS_AVAILABLE = True
except ImportError:
    UC_TOOLS_AVAILABLE = False
    print("⚠️ UC tools not available")


class AgentState(TypedDict):
    """State for the multi-agent system"""
    messages: List[Dict[str, Any]]
    current_agent: str
    context: Dict[str, Any]
    final_response: Optional[str]


@dataclass
class AgentConfig:
    """Configuration for agents"""
    name: str
    description: str
    tools: List[BaseTool]
    system_prompt: str


class MultiAgentGenieSystem:
    """Multi-agent system with Genie integration"""
    
    def __init__(self, databricks_profile: str = "DEFAULT_azure"):
        self.databricks_profile = databricks_profile
        self.agents = {}
        self.tools = []
        self.workflow = None
        
        # Initialize the system
        self._setup_agents()
        self._setup_workflow()
    
    def _setup_agents(self):
        """Setup specialized agents"""
        
        # Genie Agent - for natural language data queries
        genie_tool = create_genie_tool()
        genie_config = AgentConfig(
            name="genie_agent",
            description="Specialized agent for natural language data queries using Genie",
            tools=[genie_tool],
            system_prompt="""You are a Genie agent specialized in answering questions about healthcare data.
            Use the genie_query tool to answer questions about claims, members, providers, and other data.
            Always provide clear, structured responses with the actual data results.
            If the question is about data analysis or requires SQL queries, use the genie_query tool."""
        )
        
        # UC Functions Agent - for structured business logic
        if UC_TOOLS_AVAILABLE:
            try:
                # Define UC function names (you can customize these)
                uc_function_names = [
                    "my_catalog.payer_silver.lookup_member",
                    "my_catalog.payer_silver.lookup_claims"
                ]
                uc_toolkit = UCFunctionToolkit(function_names=uc_function_names)
                uc_tools = uc_toolkit.tools
                uc_config = AgentConfig(
                    name="uc_agent", 
                    description="Specialized agent for Unity Catalog function calls",
                    tools=uc_tools,
                    system_prompt="""You are a UC agent specialized in healthcare business logic.
                    Use the Unity Catalog functions to lookup members, claims, providers, and other business data.
                    These functions provide structured, reliable data for business operations."""
                )
            except Exception as e:
                print(f"⚠️ UC tools error: {e}")
                uc_tools = []
                uc_config = AgentConfig(
                    name="uc_agent",
                    description="UC agent (tools not available)",
                    tools=[],
                    system_prompt="UC functions are not available."
                )
        else:
            uc_tools = []
            uc_config = AgentConfig(
                name="uc_agent",
                description="UC agent (tools not available)",
                tools=[],
                system_prompt="UC functions are not available."
            )
        
        # Supervisor Agent - orchestrates the workflow
        supervisor_config = AgentConfig(
            name="supervisor",
            description="Supervisor agent that coordinates other agents",
            tools=[],
            system_prompt="""You are a supervisor agent that coordinates specialized agents.
            Based on the user's question, decide which agent(s) should handle the request:
            - For data analysis, SQL queries, or data exploration: use genie_agent
            - For member lookups, claims processing, or business logic: use uc_agent
            - For complex questions: coordinate multiple agents
            Always provide a comprehensive response combining insights from all relevant agents."""
        )
        
        self.agents = {
            "supervisor": supervisor_config,
            "genie_agent": genie_config,
            "uc_agent": uc_config
        }
        
        # Collect all tools
        self.tools = [genie_tool] + uc_tools
    
    def _setup_workflow(self):
        """Setup LangGraph workflow"""
        
        if not LANGGRAPH_AVAILABLE:
            print("⚠️ LangGraph not available, using simple fallback")
            return
        
        try:
            # Create the state graph
            workflow = StateGraph(AgentState)
            
            # Add nodes for each agent
            for agent_name, agent_config in self.agents.items():
                if agent_name == "supervisor":
                    workflow.add_node(agent_name, self._supervisor_node)
                else:
                    workflow.add_node(agent_name, self._create_agent_node(agent_config))
            
            # Add edges
            workflow.add_edge("supervisor", "genie_agent")
            workflow.add_edge("supervisor", "uc_agent")
            workflow.add_edge("genie_agent", "supervisor")
            workflow.add_edge("uc_agent", "supervisor")
            
            # Set entry point
            workflow.set_entry_point("supervisor")
            
            # Compile the workflow
            self.workflow = workflow.compile()
            
        except Exception as e:
            print(f"⚠️ Error setting up workflow: {e}")
            self.workflow = None
    
    def _supervisor_node(self, state: AgentState) -> AgentState:
        """Supervisor node that decides which agents to use"""
        
        messages = state.get("messages", [])
        if not messages:
            return state
        
        last_message = messages[-1]
        user_question = last_message.get("content", "")
        
        print(f"🎯 Supervisor analyzing question: {user_question}")
        
        # Simple routing logic
        question_lower = user_question.lower()
        
        # Determine which agents to use
        use_genie = any(keyword in question_lower for keyword in [
            "analyze", "show", "what", "how many", "distribution", "average", "total", "count",
            "data", "claims", "members", "providers", "status", "amount"
        ])
        
        use_uc = any(keyword in question_lower for keyword in [
            "lookup", "find", "get", "member", "claim", "provider", "eligibility"
        ])
        
        # Update state
        state["current_agent"] = "supervisor"
        state["context"] = {
            "use_genie": use_genie,
            "use_uc": use_uc,
            "user_question": user_question
        }
        
        print(f"📋 Supervisor decision: Genie={use_genie}, UC={use_uc}")
        
        return state
    
    def _create_agent_node(self, agent_config: AgentConfig):
        """Create an agent node for LangGraph"""
        
        def agent_node(state: AgentState) -> AgentState:
            agent_name = agent_config.name
            print(f"🤖 {agent_name} processing request...")
            
            # Check if this agent should be used
            context = state.get("context", {})
            if agent_name == "genie_agent" and not context.get("use_genie", False):
                print(f"⏭️ Skipping {agent_name} (not needed)")
                return state
            
            if agent_name == "uc_agent" and not context.get("use_uc", False):
                print(f"⏭️ Skipping {agent_name} (not needed)")
                return state
            
            # Process with the agent
            try:
                if agent_config.tools:
                    # Use tools to process the request
                    for tool in agent_config.tools:
                        if hasattr(tool, '_run'):
                            result = tool._run(context.get("user_question", ""))
                            print(f"✅ {agent_name} result: {result[:100]}...")
                            
                            # Add result to context
                            if "agent_results" not in state["context"]:
                                state["context"]["agent_results"] = {}
                            state["context"]["agent_results"][agent_name] = result
                else:
                    print(f"⚠️ {agent_name} has no tools available")
                    
            except Exception as e:
                print(f"❌ Error in {agent_name}: {e}")
                state["context"]["agent_results"] = state.get("context", {}).get("agent_results", {})
                state["context"]["agent_results"][agent_name] = f"Error: {str(e)}"
            
            return state
        
        return agent_node
    
    def process_query(self, question: str) -> str:
        """Process a user query through the multi-agent system"""
        
        print(f"🚀 Processing query: {question}")
        
        if not LANGGRAPH_AVAILABLE or not self.workflow:
            # Fallback to simple processing
            return self._simple_process(question)
        
        try:
            # Create initial state
            initial_state = AgentState(
                messages=[{"role": "user", "content": question}],
                current_agent="supervisor",
                context={},
                final_response=None
            )
            
            # Run the workflow
            result = self.workflow.invoke(initial_state)
            
            # Compile final response
            return self._compile_response(result)
            
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            return self._simple_process(question)
    
    def _simple_process(self, question: str):
        """Simple fallback processing without LangGraph"""
        
        print("🔄 Using simple processing (LangGraph not available)")
        
        results = []
        
        # Try Genie first
        try:
            genie_tool = create_genie_tool()
            genie_result = genie_tool._run(question)
            
            # Format the Genie result properly
            formatted_result = self._format_genie_response(genie_result, question)
            
            # Check if it's structured data (dict) or text
            if isinstance(formatted_result, dict):
                print(f"🔍 Debug: Returning structured data: {formatted_result}")
                return formatted_result  # Return structured data directly
            else:
                print(f"🔍 Debug: Adding text result: {formatted_result}")
                results.append(formatted_result)
        except Exception as e:
            print(f"⚠️ Genie error: {e}")
        
        # Try UC functions if available
        if UC_TOOLS_AVAILABLE:
            try:
                # Simple UC processing would go here
                results.append("**UC Functions:** Available but not implemented in simple mode")
            except Exception as e:
                print(f"⚠️ UC tools error: {e}")
        else:
            results.append("**UC Functions:** Not available")
        
        return "\n\n".join(results) if results else "No results available"
    
    def _format_genie_response(self, response: str, question: str = "") -> str:
        """Format Genie response with proper table display"""
        
        # Check if this is the old format with inline data
        if "Data (" in response and "• Row" in response:
            print("🔄 Converting old format to new display...")
            
            # Extract data from the inline format
            data_rows = []
            
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
                            print(f"Could not parse row: {part[:50]}...")
                            continue
            
            # Create a formatted response with table
            if data_rows:
                import pandas as pd
                df = pd.DataFrame(data_rows)
                
                # Add column names
                if len(df.columns) >= 2:
                    df.columns = ['Status', 'Count'] if 'claim_status' in response else ['Status', 'Total']
                
                # Create formatted response with structured data for Streamlit
                formatted_response = f"""## 🔮 Genie Analysis
**Query:** {question}
**Status:** COMPLETED

### 📊 Results Table
Status Count {df.to_string(index=False, header=False)}

**Summary:** Found {len(df)} records
"""
                return formatted_response
        
        # Return original response if no conversion needed
        return f"**Genie Analysis:**\n{response}"
    
    def _compile_response(self, result: AgentState) -> str:
        """Compile final response from agent results"""
        
        context = result.get("context", {})
        agent_results = context.get("agent_results", {})
        
        if not agent_results:
            return "No results from agents."
        
        response_parts = []
        response_parts.append("## Multi-Agent Analysis Results\n")
        
        for agent_name, agent_result in agent_results.items():
            response_parts.append(f"### {agent_name.replace('_', ' ').title()}")
            response_parts.append(agent_result)
            response_parts.append("")
        
        return "\n".join(response_parts)


def create_multiagent_system(databricks_profile: str = "DEFAULT_azure") -> MultiAgentGenieSystem:
    """Create a multi-agent system instance"""
    return MultiAgentGenieSystem(databricks_profile)


# Test function
def test_multiagent_system():
    """Test the multi-agent system"""
    print("🧪 Testing Multi-Agent Genie System")
    print("=" * 50)
    
    system = create_multiagent_system()
    
    # Test queries
    test_questions = [
        "What are the different statuses of claims and how many claims fall under each status?",
        "Show me the top 5 claims by amount",
        "Lookup member information for member ID 12345"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Testing: {question}")
        result = system.process_query(question)
        print(f"Result: {result[:200]}...")
        print("-" * 50)


if __name__ == "__main__":
    test_multiagent_system()
