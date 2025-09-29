# 🏥 Healthcare Payor AI System - Complete Documentation

## 📋 Quick Reference

### **Default Configuration**
When running `python start_healthcare_app.py` without arguments:

| Parameter | Default Value | Environment Variable |
|-----------|---------------|---------------------|
| **Conda Environment** | `azure_databricks` | `CONDA_ENV` |
| **Catalog** | `my_catalog` | `HEALTHCARE_CATALOG` |
| **Schema** | `payer_silver` | `HEALTHCARE_SCHEMA` |
| **Databricks Profile** | `DEFAULT` (local only) | `HEALTHCARE_DATABRICKS_PROFILE` |
| **LLM Endpoint** | `databricks-meta-llama-3-3-70b-instruct` | `HEALTHCARE_LLM_ENDPOINT` |
| **LLM Temperature** | `0.1` | `HEALTHCARE_LLM_TEMPERATURE` |
| **Port** | `8501` | `STREAMLIT_PORT` |
| **Host** | `localhost` | `STREAMLIT_HOST` |
| **Debug Mode** | `false` | `HEALTHCARE_DEBUG` |

## 🚀 Startup Commands

### **Basic Usage**
```bash
# Use all defaults
python start_healthcare_app.py

# Or use shell script
./start_app.sh
```

### **Custom Configuration**
```bash
# Custom catalog and schema
python start_healthcare_app.py --catalog my_catalog --schema payer_silver

# Different LLM endpoint
python start_healthcare_app.py --llm-endpoint databricks-claude-3-5-sonnet

# Custom port and debug
python start_healthcare_app.py --port 8502 --debug

# Test connections first
python start_healthcare_app.py --test-connection
```

### **Environment Variables**
```bash
export HEALTHCARE_CATALOG="my_catalog"
export HEALTHCARE_SCHEMA="payer_silver"
export HEALTHCARE_LLM_ENDPOINT="databricks-meta-llama-3-3-70b-instruct"
python start_healthcare_app.py
```

## 🛠️ System Architecture

### **Components**
1. **Streamlit App** (`healthcare_payor_streamlit_app.py`)
   - Web interface for user interactions
   - Chat interface with AI agent
   - Sidebar quick actions

2. **Healthcare Payor Agent** (`HealthcarePayorAgent` class)
   - Databricks client initialization
   - UC tools setup
   - LangChain agent creation

3. **Unity Catalog Tools**
   - `lookup_member`: Member information lookup
   - `lookup_claims`: Claims history retrieval
   - `lookup_providers`: Provider network search

4. **Databricks Integration**
   - LLM: `databricks-meta-llama-3-3-70b-instruct`
   - UC Functions: `my_catalog.payer_silver.*`
   - Authentication: `DEFAULT` profile

### **Data Flow**
```
User Query → Streamlit → LangChain Agent → UC Tools → Database → LLM → Response
```

## 🔧 Configuration Details

### **Databricks LLM Integration**
- **Location**: `healthcare_payor_streamlit_app.py` lines 84-87
- **LLM Initialization**: `ChatDatabricks(endpoint=self.llm_endpoint, temperature=self.llm_temperature)`
- **Agent Creation**: `create_tool_calling_agent(self.llm, self.tools, prompt)`
- **Execution**: `agent_executor.invoke({"input": user_input})`
- **Authentication**: Works for both local (with profile) and cloud (default auth)

### **UC Tools Registration**
- **Location**: `healthcare_payor_streamlit_app.py` lines 60-66
- **Function Names**: 
  - `my_catalog.payer_silver.lookup_member`
  - `my_catalog.payer_silver.lookup_claims`
  - `my_catalog.payer_silver.lookup_providers`
- **Toolkit**: `UCFunctionToolkit(function_names=function_names)`
- **Agent Integration**: `AgentExecutor(agent=agent, tools=self.tools)`

## 🧪 Test Questions

### **Member Services**
```
"Look up member M001"
"What are the benefits for member M001?"
"Show me the claims history for member M001"
```

### **Provider Relations**
```
"Find cardiology providers in my network"
"Search for providers specializing in dermatology"
```

### **Health Guidance**
```
"I have chest pain, what should I do?"
"What are the symptoms of diabetes?"
"I have a headache, should I see a doctor?"
```

## 📁 Project Structure

```
payor-billing-customer-care/
├── healthcare_payor_streamlit_app.py    # Main Streamlit app
├── start_healthcare_app.py              # Python startup script
├── start_app.sh                         # Shell startup script
├── requirements.txt                     # Dependencies
├── README.md                           # Project overview
├── STARTUP_GUIDE.md                    # Startup documentation
├── DOCUMENTATION.md                    # This file
└── notebooks/
    ├── 02_define_uc_tools_payor.ipynb  # UC functions definition
    └── 03_agent_deployment_and_evaluation.ipynb  # Agent setup
```

## 🔍 Troubleshooting

### **Common Issues**

#### **ModuleNotFoundError: No module named 'databricks_langchain'**
```bash
# Solution: Use conda environment
conda run -n azure_databricks streamlit run healthcare_payor_streamlit_app.py

# Or install packages
conda run -n azure_databricks pip install databricks-langchain unitycatalog-langchain[databricks]
```

#### **Databricks Connection Failed**
```bash
# Check Databricks CLI configuration
databricks configure

# Test connection
databricks workspace ls
```

#### **UC Functions Not Found**
```bash
# Ensure functions are created in the correct schema
# Run the notebook: 02_define_uc_tools_payor.ipynb
```

### **Debug Mode**
```bash
# Enable debug logging
python start_healthcare_app.py --debug

# Test connections
python start_healthcare_app.py --test-connection
```

## 🚀 Deployment Scenarios

### **Development**
```bash
python start_healthcare_app.py --debug --test-connection
```

### **Staging**
```bash
python start_healthcare_app.py --catalog staging_catalog --schema healthcare_data --port 8502
```

### **Production**
```bash
python start_healthcare_app.py \
  --catalog production_catalog \
  --schema healthcare_data \
  --llm-endpoint databricks-claude-3-5-sonnet \
  --port 8080 \
  --host 0.0.0.0
```

## 🔧 Environment Setup

### **Prerequisites**
1. **Conda Environment**: `azure_databricks`
2. **Databricks CLI**: Configured with `DEFAULT` profile
3. **Required Packages**: `databricks-langchain`, `unitycatalog-langchain[databricks]`, `langchain`, `streamlit`

### **Installation**
```bash
# Create conda environment
conda create -n azure_databricks python=3.10

# Install packages
conda run -n azure_databricks pip install databricks-langchain unitycatalog-langchain[databricks] langchain streamlit

# Configure Databricks CLI
databricks configure
```

## 📊 Monitoring and Logging

### **Health Checks**
- ✅ Databricks workspace connection
- ✅ UC functions availability
- ✅ LLM endpoint accessibility
- ✅ Required packages installation

### **Debug Information**
- **Connection Status**: Displayed in Streamlit sidebar
- **Tool Loading**: Shows number of UC tools loaded
- **Agent Status**: Confirms agent initialization
- **Error Handling**: Graceful error recovery

## 🎯 Best Practices

### **Configuration Management**
1. **Use environment variables** for different deployments
2. **Test connections** before production deployment
3. **Enable debug mode** for troubleshooting
4. **Monitor resource usage** for LLM endpoints

### **Security**
1. **Use Databricks profiles** for authentication
2. **Limit UC function access** to necessary schemas
3. **Monitor LLM usage** and costs
4. **Implement proper error handling**

### **Performance**
1. **Cache responses** for common queries
2. **Optimize UC function queries**
3. **Monitor LLM response times**
4. **Use appropriate temperature settings**

## 📞 Support Information

### **Key Files**
- **Main App**: `healthcare_payor_streamlit_app.py`
- **Startup Script**: `start_healthcare_app.py`
- **UC Functions**: `notebooks/02_define_uc_tools_payor.ipynb`
- **Documentation**: `DOCUMENTATION.md`

### **Configuration Files**
- **Requirements**: `requirements.txt`
- **Startup Guide**: `STARTUP_GUIDE.md`
- **Project README**: `README.md`

### **Quick Commands**
```bash
# Start with defaults
python start_healthcare_app.py

# Start with custom config
python start_healthcare_app.py --catalog my_catalog --schema payer_silver

# Test everything
python start_healthcare_app.py --test-connection --debug
```

---

**🏥 Healthcare Payor AI System - Complete Documentation**  
**Last Updated**: $(date)  
**Version**: 1.0  
**Status**: Production Ready ✅
