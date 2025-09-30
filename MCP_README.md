# Healthcare Payor AI System - MCP Integration

## 🚀 Overview

This implementation integrates **Managed MCP (Model Context Protocol) servers** with the Healthcare Payor AI System, providing seamless access to Databricks Genie and Unity Catalog Functions through standardized MCP interfaces.

## 🔧 MCP Servers Integrated

### 1. Genie MCP Server
- **URL:** `https://adb-984752964297111.11.azuredatabricks.net/api/2.0/mcp/genie/01f06a3068a81406a386e8eaefc74545`
- **Purpose:** Natural language queries for structured data analysis
- **Capabilities:** Advanced analytics, data insights, table exploration

### 2. Unity Catalog Functions MCP Server
- **URL:** `https://adb-984752964297111.11.azuredatabricks.net/api/2.0/mcp/functions/my_catalog/payer_silver`
- **Purpose:** Execute Unity Catalog functions for data operations
- **Capabilities:** Member lookup, claims lookup, provider lookup

## 📁 File Structure

```
hospital_ai_system/
├── mcp_genie_client.py              # Genie MCP client implementation
├── mcp_uc_functions_client.py       # UC Functions MCP client implementation
├── enhanced_healthcare_payor_app_mcp.py  # Main Streamlit app with MCP
├── requirements-mcp.txt             # MCP-specific dependencies
├── start_mcp_app.sh                 # MCP app startup script
└── MCP_README.md                    # This documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Databricks CLI configured with profile `DEFAULT_azure`
- Access to the specified Databricks workspace

### Setup
1. **Install MCP dependencies:**
   ```bash
   pip install -r requirements-mcp.txt
   ```

2. **Verify Databricks authentication:**
   ```bash
   databricks auth login --host https://adb-984752964297111.11.azuredatabricks.net
   ```

3. **Test MCP connections:**
   ```bash
   python mcp_genie_client.py
   python mcp_uc_functions_client.py
   ```

## 🚀 Running the Application

### Quick Start
```bash
./start_mcp_app.sh
```

### Manual Start
```bash
# Activate conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate azure_databricks_py311

# Set Databricks profile
export DATABRICKS_PROFILE="DEFAULT_azure"

# Run the app
streamlit run enhanced_healthcare_payor_app_mcp.py --server.port 8503
```

## 🔧 MCP Client Architecture

### Genie MCP Client (`mcp_genie_client.py`)
```python
class GenieMCPClient:
    def __init__(self, workspace_hostname, genie_space_id, profile)
    def query_genie(self, query: str) -> Dict[str, Any]
    def list_tools(self) -> List[Dict[str, Any]]
    def get_health_status(self) -> Dict[str, Any]
```

### UC Functions MCP Client (`mcp_uc_functions_client.py`)
```python
class UCFunctionsMCPClient:
    def __init__(self, workspace_hostname, catalog, schema, profile)
    def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]
    def lookup_member(self, input_id: str) -> Dict[str, Any]
    def lookup_claims(self, member_id: str) -> Dict[str, Any]
    def lookup_providers(self, specialty_filter: str) -> Dict[str, Any]
```

## 🎯 Features

### 1. **Unified Tool Interface**
- Single LangChain agent with multiple MCP tools
- Automatic tool selection based on user queries
- Seamless integration between Genie and UC Functions

### 2. **Real-time Status Monitoring**
- MCP server health checks
- Tool availability monitoring
- Connection status dashboard

### 3. **Advanced Analytics**
- Genie-powered data analysis
- Natural language query processing
- Structured data insights

### 4. **Data Operations**
- Member information lookup
- Claims processing
- Provider directory search

## 🔍 Usage Examples

### Genie Queries
```python
# Natural language data analysis
genie_client = get_genie_mcp_client()
result = genie_client.query_genie("What are the top 5 claims by amount?")
```

### UC Functions
```python
# Member lookup
uc_client = get_uc_functions_mcp_client()
member = uc_client.lookup_member("1001")
claims = uc_client.lookup_claims("1001")
providers = uc_client.lookup_providers("cardiology")
```

## 🚨 Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Verify Databricks authentication
   - Check workspace hostname and space IDs
   - Ensure proper network access

2. **Tool Not Found**
   - Verify UC functions exist in the specified catalog/schema
   - Check Genie space permissions
   - Review MCP server URLs

3. **Authentication Errors**
   - Run `databricks auth login` to refresh tokens
   - Verify profile name matches configuration
   - Check workspace permissions

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from mcp_genie_client import test_genie_connection
from mcp_uc_functions_client import test_uc_functions_connection

test_genie_connection()
test_uc_functions_connection()
```

## 📊 Performance Considerations

- **MCP servers** provide optimized data access
- **Caching** implemented for repeated queries
- **Error handling** with graceful fallbacks
- **Connection pooling** for better performance

## 🔒 Security

- **OAuth authentication** required for all MCP connections
- **Workspace-level permissions** enforced
- **Secure token management** through Databricks SDK
- **No hardcoded credentials** in the code

## 🚀 Next Steps

1. **Vector Search Integration:** Add vector search MCP server for document analysis
2. **Custom MCP Servers:** Implement custom MCP servers for specific business logic
3. **Multi-agent Architecture:** Extend to multiple specialized agents
4. **Production Deployment:** Deploy to Databricks Apps for production use

## 📚 References

- [Databricks Managed MCP Servers](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/mcp/managed-mcp)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Databricks MCP Python Library](https://pypi.org/project/databricks-mcp/)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Databricks MCP documentation
3. Verify workspace permissions and configuration
4. Test individual MCP client connections
