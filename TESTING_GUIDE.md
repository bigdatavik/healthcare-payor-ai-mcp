# 🧪 Multi-Agent Healthcare System Testing Guide

## Overview
This guide explains how to test the multi-agent healthcare system to verify that it's actually using AI agents and working correctly.

## 🚀 Quick Start Testing

### 1. Start the Application
```bash
cd /Users/vik.malhotra/hospital_ai_system/payor-billing-customer-care
conda run -n azure_databricks python start_healthcare_app.py --enhanced --conda-env azure_databricks --databricks-profile DEFAULT_azure --port 8501
```

### 2. Access the Application
Open your browser and go to: `http://localhost:8501`

## 🔍 Agent Testing Scenarios

### Test 1: Genie Agent (Data Analysis Queries)
**Purpose:** Verify that data analysis queries are routed to the Genie agent

**Test Questions:**
1. "What are the different statuses of claims and how many claims fall under each status?"
2. "Show me the top 5 claims by amount"
3. "What is the average claim amount by provider?"
4. "How many members do we have in each plan?"
5. "What is the distribution of total charges for claims?"

**Expected Behavior:**
- ✅ Should automatically use Genie tool
- ✅ Should return structured data (tables, charts)
- ✅ Should show "🔮 Genie Analysis" in response
- ✅ Should display actual data from your Databricks workspace

### Test 2: UC Functions Agent (Business Logic Queries)
**Purpose:** Verify that business logic queries are routed to UC Functions

**Test Questions:**
1. "Lookup member information for member ID 1001"
2. "Show me claims for member 1001"
3. "Find providers by specialty cardiology"
4. "Check eligibility for member 1001"
5. "Get benefits for member 1001"

**Expected Behavior:**
- ✅ Should automatically use UC Functions
- ✅ Should return structured member/claims/provider data
- ✅ Should show specific entity information
- ✅ Should use business logic functions

### Test 3: Agent Tool Selection
**Purpose:** Verify that the system automatically chooses the right agent

**Test Questions:**
1. "What are the different statuses of claims?" → Should use **Genie**
2. "Lookup member 12345" → Should use **UC Functions**
3. "Show me analytics dashboard" → Should use **Genie**
4. "Find member details for ID 67890" → Should use **UC Functions**

**Expected Behavior:**
- ✅ System should automatically route to appropriate agent
- ✅ No manual agent selection required
- ✅ Seamless user experience

## 🛠️ Technical Testing

### Test Agent Components
```bash
# Run the agent proof test
conda run -n azure_databricks python test_agents_proof.py
```

**Expected Output:**
```
🎉 PROOF COMPLETE: System is using real agents!
✅ Genie Agent: Working
✅ Multi-Agent System: Working
✅ Agent Tools: Working
```

### Test Individual Components
```bash
# Test Genie tool directly
conda run -n azure_databricks python -c "
from genie_multiagent_tool import create_genie_tool
tool = create_genie_tool()
print(f'Genie tool: {tool.name}')
print(f'Description: {tool.description}')
"

# Test multi-agent system
conda run -n azure_databricks python -c "
from langgraph_genie_multiagent import create_multiagent_system
system = create_multiagent_system()
print(f'Multi-agent system: {type(system).__name__}')
"
```

## 📊 Verification Checklist

### ✅ Agent Verification
- [ ] Genie agent is loaded and functional
- [ ] UC Functions agent is loaded and functional
- [ ] Multi-agent system routes queries correctly
- [ ] Tools are properly integrated
- [ ] No manual agent selection required

### ✅ Data Verification
- [ ] Genie queries return real data from Databricks
- [ ] UC Functions return structured business data
- [ ] Tables and charts are displayed properly
- [ ] Data is accurate and up-to-date

### ✅ User Experience
- [ ] Single interface for all queries
- [ ] Automatic tool selection
- [ ] Input field clears after queries
- [ ] Professional healthcare responses
- [ ] Role-based prompts working

## 🐛 Troubleshooting

### Common Issues

**Issue:** "Genie tool not available"
**Solution:** Check Databricks authentication and Genie workspace access

**Issue:** "UC Functions not available"
**Solution:** Verify Unity Catalog functions are created and accessible

**Issue:** "No agents loaded"
**Solution:** Check conda environment and dependencies

**Issue:** "Input field not clearing"
**Solution:** This is fixed in the current version with form-based input

### Debug Mode
Enable debug mode to see detailed agent activity:
```bash
export HEALTHCARE_DEBUG=true
conda run -n azure_databricks python start_healthcare_app.py --enhanced --conda-env azure_databricks --databricks-profile DEFAULT_azure --port 8501
```

## 📈 Performance Testing

### Load Testing
1. **Multiple concurrent queries**
2. **Different question types**
3. **Long conversation history**
4. **Role switching**

### Response Time Testing
- **Genie queries:** Should complete within 30-60 seconds
- **UC Functions:** Should complete within 5-10 seconds
- **Simple queries:** Should complete within 2-5 seconds

## 🎯 Success Criteria

### ✅ System is Working if:
1. **Agents are loaded** - No "agent not available" errors
2. **Tool selection works** - Right agent chosen for each query type
3. **Data is returned** - Real data from Databricks, not mock responses
4. **UI is responsive** - Input clears, conversations work smoothly
5. **Professional responses** - Healthcare-appropriate language and formatting

### ❌ System Issues if:
1. **No agents loaded** - All queries fail or return generic responses
2. **Wrong tool selection** - Data queries go to UC Functions, lookups go to Genie
3. **Mock responses** - No real data, just placeholder text
4. **UI problems** - Input doesn't clear, conversations don't work
5. **Generic responses** - Not healthcare-specific, no tool usage

## 🔧 Advanced Testing

### Test Agent Orchestration
```python
# Test the multi-agent workflow
from langgraph_genie_multiagent import create_multiagent_system

system = create_multiagent_system()
response = system.process_query("What are the different statuses of claims?")
print(f"Response: {response}")
```

### Test Tool Integration
```python
# Test individual tools
from genie_multiagent_tool import create_genie_tool

genie_tool = create_genie_tool()
result = genie_tool._run("What are the different statuses of claims?")
print(f"Genie result: {result}")
```

## 📝 Test Results Template

### Test Session Results
```
Date: ___________
Tester: ___________
Environment: ___________

✅ Genie Agent Tests:
- [ ] Data analysis queries work
- [ ] Returns structured data
- [ ] Shows proper formatting

✅ UC Functions Tests:
- [ ] Business logic queries work
- [ ] Returns entity data
- [ ] Uses proper functions

✅ Multi-Agent Tests:
- [ ] Automatic tool selection
- [ ] Seamless user experience
- [ ] No manual intervention

✅ UI Tests:
- [ ] Input clearing works
- [ ] Conversations persist
- [ ] Professional interface

Overall Result: ✅ PASS / ❌ FAIL
Notes: ___________
```

## 🎉 Conclusion

This testing guide ensures that the multi-agent healthcare system is working correctly with real AI agents, proper tool selection, and professional healthcare responses. The system should provide a seamless experience where users can ask any healthcare question and get the appropriate response from the right agent.
