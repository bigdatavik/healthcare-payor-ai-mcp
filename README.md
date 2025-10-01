# Healthcare Payor AI System with MCP Integration

<img src="https://raw.githubusercontent.com/databricks-industry-solutions/.github/main/profile/solacc_logo.png" width="600px">

## 🏥 Business Problem

Healthcare payors face significant challenges in managing member inquiries, claims processing, and provider management at scale. This solution leverages AI and **Model Context Protocol (MCP)** to create an intelligent healthcare payor system that provides:

- **Automated member support** with AI-powered responses
- **Real-time claims analysis** and processing insights
- **Provider directory management** and specialty searches
- **Unified data access** through MCP server integration
- **Scalable deployment** on Databricks Apps platform

## 🚀 Overview

This implementation integrates **Managed MCP (Model Context Protocol) servers** with a comprehensive Healthcare Payor AI System, providing seamless access to Databricks services through standardized MCP interfaces. The system is designed for deployment on [Databricks Apps](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/), eliminating the need for separate infrastructure while maintaining enterprise-grade security and compliance.

### Key Features
- **MCP Server Integration**: Genie, Unity Catalog Functions, and Knowledge Assistant
- **Centralized Configuration**: Easy local/cloud deployment switching
- **Clean User Interface**: Professional responses without technical clutter
- **Cloud-Native**: Built for Databricks Apps deployment
- **Enterprise Security**: OAuth authentication and workspace-level permissions

## 🔧 MCP Servers Integrated

### 1. Genie MCP Server
- **Purpose**: Natural language queries for structured data analysis
- **Capabilities**: Advanced analytics, data insights, table exploration
- **Integration**: Direct access to Databricks Genie space

### 2. Unity Catalog Functions MCP Server
- **Purpose**: Execute Unity Catalog functions for data operations
- **Capabilities**: Member lookup, claims lookup, provider lookup
- **Integration**: Seamless access to governed data functions

### 3. Knowledge Assistant MCP Server
- **Purpose**: Unstructured text analysis and document processing
- **Capabilities**: FAQ retrieval, document search, knowledge extraction
- **Integration**: AI-powered knowledge management

## 📁 Repository Structure

```
healthcare-payor-ai-mcp/
├── enhanced_healthcare_payor_app_mcp.py    # Main Streamlit application
├── config.py                               # Centralized configuration
├── app.yaml                               # Databricks Apps deployment config
├── app.yaml.example                       # Deployment template
├── mcp_genie_client.py                    # Genie MCP client
├── mcp_uc_functions_client.py             # UC Functions MCP client
├── mcp_knowledge_assistant_client.py      # Knowledge Assistant MCP client
├── start_mcp_app.sh                       # Local startup script
├── requirements.txt                       # Python dependencies
├── databricks.yml                         # Databricks bundle configuration
└── README.md                              # This documentation
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python**: 3.11+
- **Databricks Workspace**: With Unity Catalog enabled
- **Databricks CLI**: Configured with appropriate profile
- **Access**: To MCP servers and Unity Catalog functions

### Initial Data Setup

Before running the Healthcare Payor AI System, you need to set up the initial catalog, schema, and tables. Follow these steps:

1. **Set up the base data structure using the medallion architecture:**
   ```bash
   # Clone the databricksfirststeps repository for initial setup
   git clone https://github.com/bigdatavik/databricksfirststeps.git
   cd databricksfirststeps
   ```

2. **Run the medallion ETL notebook in Databricks:**
   - Import `payer_medallion_Load_sparkSQL.ipynb` to your Databricks workspace
   - Execute the notebook to create the Bronze/Silver/Gold layers
   - This will create the necessary catalog, schema, and base tables

3. **Create Unity Catalog Functions (UDFs):**
   ```bash
   # Navigate to the healthcare system directory
   cd /path/to/healthcare-payor-ai-mcp
   
   # Run the UDF creation notebook
   # In Databricks, open: notebooks/02_define_uc_tools_payor.ipynb
   # Execute the notebook to create all required Unity Catalog functions
   ```

   This notebook will create the following UDFs:
   - `get_member_details()` - Member information lookup
   - `get_claims_by_member()` - Claims retrieval by member
   - `get_provider_info()` - Provider directory search
   - `search_claims_by_diagnosis()` - Claims search by diagnosis
   - `get_member_claim_summary()` - Member claim summaries

4. **Create Genie Room for Analytics:**
   ```bash
   # In Databricks workspace, navigate to Genie
   # 1. Go to the Genie section in your Databricks workspace
   # 2. Click "Create Room" or "New Room"
   # 3. Configure the room with the following settings:
   ```

   **Genie Room Configuration:**
   - **Room Name**: `Healthcare Payor Analytics`
   - **Description**: `Analytics room for healthcare payor data analysis`
   - **Data Sources**: Add the following tables from `payer_gold` schema:
     - `claims_enriched` - Enriched claims data with member and provider details
     - `member_claim_summary` - Aggregated member claim summaries
   - **Access Level**: Set appropriate permissions for your team

   **Get the Genie Space ID:**
   ```bash
   # After creating the room, copy the Space ID from the URL
   # The URL will look like: https://your-workspace/workspace/notebooks/.../genie/space/01f06a3068a81406a386e8eaefc74545
   # Copy the Space ID: 01f06a3068a81406a386e8eaefc74545
   ```

5. **Set up Knowledge Assistant using Agent Bricks:**
   
   **Prerequisites:**
   - Ensure your workspace has **Mosaic AI Agent Bricks Preview (Beta)** enabled
   - **Production monitoring for MLflow (Beta)** enabled for tracing
   - **Serverless compute** enabled
   - **Unity Catalog** enabled
   - **Partner-powered AI features** enabled
   - Access to **Mosaic AI Model Serving**
   - Access to foundation models in Unity Catalog through the `system.ai` schema
   - Access to a **serverless budget policy** with a nonzero budget
   - Workspace in supported regions: `centralus`, `eastus`, `eastus2`, `northcentralus`, `southcentralus`, `westus`, or `westus2`

   **Step 1: Prepare Knowledge Source Files**
   ```bash
   # Upload the following .txt files to a Unity Catalog volume in payer_bronze schema
   # These files contain healthcare payor domain knowledge:
   ```

   **Knowledge Source Files:**
   - **`member_benefits.txt`** - Member benefit plans, coverage details, and eligibility requirements
   - **`claims_processing.txt`** - Claims processing procedures, approval workflows, and denial reasons
   - **`provider_network.txt`** - Provider directory information, specialties, and network coverage
   - **`medical_coding.txt`** - ICD-10 codes, CPT codes, and medical terminology reference
   - **`policy_guidelines.txt`** - Healthcare policies, compliance requirements, and operational procedures
   - **`faq_common_questions.txt`** - Frequently asked questions and standard responses
   - **`coverage_limits.txt`** - Coverage limits, deductibles, copayments, and out-of-pocket maximums
   - **`prior_authorization.txt`** - Prior authorization requirements and procedures

   **Step 2: Create Knowledge Assistant Agent**
   ```bash
   # In Databricks workspace:
   # 1. Navigate to "Agents" in the left navigation pane
   # 2. Click "Knowledge Assistant"
   # 3. Configure your agent:
   ```

   **Agent Configuration:**
   - **Name**: `Healthcare Payor Knowledge Assistant`
   - **Description**: `AI-powered knowledge base for healthcare payor operations, member support, and claims processing`
   - **Knowledge Source Type**: `UC Files`
   - **Source**: Select the Unity Catalog volume containing your .txt files
   - **Name**: `Healthcare Payor Documentation`
   - **Content Description**: `Healthcare payor operations documentation including member benefits, claims processing, provider networks, medical coding, policies, FAQs, coverage limits, and prior authorization procedures`

   **Step 3: Add Instructions (Optional)**
   ```bash
   # Add specific instructions for the agent's behavior:
   # "You are a healthcare payor knowledge assistant. Provide accurate, helpful responses about:
   # - Member benefits and coverage details
   # - Claims processing procedures and requirements
   # - Provider network information and specialties
   # - Medical coding and terminology
   # - Policy guidelines and compliance requirements
   # - Common questions and standard procedures
   # Always cite your sources and provide specific, actionable information."
   ```

   **Step 4: Test and Improve the Agent**
   ```bash
   # After agent creation (can take up to a few hours):
   # 1. Go to the "Configure" tab of your Knowledge Assistant
   # 2. Click "Try in Playground" to test the agent
   # 3. Ask questions related to your healthcare payor documentation
   # 4. Review responses and citations
   # 5. Use "Improve quality" tab to add questions for labeling sessions
   # 6. Gather feedback from subject matter experts to improve performance
   ```

   **Step 5: Get the Endpoint ID**
   ```bash
   # 1. Go to the "Configure" tab of your Knowledge Assistant
   # 2. Click "Open in playground"
   # 3. Click "Get code" and select "Python API"
   # 4. Copy the endpoint ID from the code example
   # The endpoint ID will look like: ka-d0808962-endpoint
   ```

   **Step 6: Quality Improvement (Optional)**
   ```bash
   # Use the "Improve quality" tab to:
   # 1. Add at least 20 questions for evaluation
   # 2. Start a labeling session
   # 3. Share the review app with healthcare domain experts
   # 4. Collect feedback to improve agent performance
   # 5. Merge feedback and retrain the agent
   ```

6. **Update Configuration with MCP Server IDs:**
   ```bash
   # Update app.yaml with your MCP server IDs
   # Edit the following values in app.yaml:
   env:
     - name: 'GENIE_SPACE_ID'
       value: 'your-actual-genie-space-id'  # Replace with your Genie Space ID
     - name: 'KNOWLEDGE_ASSISTANT_ENDPOINT_ID'
       value: 'your-actual-endpoint-id'     # Replace with your Knowledge Assistant endpoint ID
   
   # Also update config.py for local development:
   # Edit config.py and update both GENIE_SPACE_ID and KNOWLEDGE_ASSISTANT_ENDPOINT_ID
   ```

7. **Verify setup:**
   - Ensure your catalog and schema are created
   - Verify all UDFs are accessible
   - Confirm data is loaded in the Silver/Gold layers
   - Test Genie room access with sample queries
   - Verify Space ID is correctly configured in both app.yaml and config.py

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bigdatavik/healthcare-payor-ai-mcp.git
   cd healthcare-payor-ai-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system:**
   ```bash
   # Edit config.py with your values
   python config.py  # Validate configuration
   ```

4. **Start the application:**
   ```bash
   ./start_mcp_app.sh
   ```

### Databricks Apps Deployment

The system is optimized for deployment on [Databricks Apps](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/), which provides:

- **Serverless hosting** on Azure Databricks platform
- **Integrated security** with OAuth and service principals
- **Automatic scaling** and resource management
- **Built-in compliance** and governance

#### Deployment Steps

1. **Prepare your workspace:**
   - Ensure you have Databricks Apps access
   - Verify Unity Catalog is enabled
   - Confirm MCP server access

2. **Configure deployment:**
   ```bash
   # Copy and edit the deployment configuration
   cp app.yaml.example app.yaml
   # Update environment variables in app.yaml
   ```

3. **Deploy using Databricks CLI:**
   ```bash
   databricks apps deploy
   ```

## ⚙️ Configuration

### Centralized Configuration (`config.py`)

The system uses a centralized configuration approach that supports both local development and cloud deployment:

```python
# Unity Catalog Configuration
CATALOG_NAME = "my_catalog"
SCHEMA_NAME = "payer_silver"

# Databricks Configuration
DATABRICKS_PROFILE = "DEFAULT_azure"
WORKSPACE_HOSTNAME = "your-workspace.azuredatabricks.net"

# Genie Configuration
GENIE_SPACE_ID = "your_genie_space_id"

# Knowledge Assistant Configuration
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "your_endpoint_id"
```

### Environment Variable Override

For cloud deployment, the system automatically detects and uses environment variables:

```yaml
# app.yaml
env_variables:
  - name: 'CATALOG_NAME'
    value: 'my_catalog'
  - name: 'SCHEMA_NAME'
    value: 'payer_silver'
  - name: 'GENIE_SPACE_ID'
    value: 'your_genie_space_id'
  - name: 'KNOWLEDGE_ASSISTANT_ENDPOINT_ID'
    value: 'your_endpoint_id'
```

### Auto-Detection Features

- **Workspace Hostname**: Automatically detected in cloud environments
- **Databricks Profile**: Auto-detected for seamless authentication
- **MCP Server URLs**: Constructed automatically from workspace configuration

## 🚀 Running the Application

### Local Development
```bash
# Quick start
./start_mcp_app.sh

# Manual start
streamlit run enhanced_healthcare_payor_app_mcp.py --server.port 8503
```

### Cloud Deployment (Databricks Apps)
```bash
# Deploy to Databricks Apps
databricks apps deploy

# Monitor deployment
databricks apps list
databricks apps get <app-id>
```

## 🎯 Features

### 1. **Unified AI Agent Interface**
- Single LangChain agent with multiple MCP tools
- Automatic tool selection based on user queries
- Seamless integration between all MCP servers

### 2. **Real-time Status Monitoring**
- MCP server health checks
- Tool availability monitoring
- Connection status dashboard

### 3. **Advanced Data Analytics**
- Genie-powered natural language queries
- Structured data insights and visualizations
- Real-time data processing

### 4. **Healthcare-Specific Operations**
- Member information lookup and management
- Claims processing and analysis
- Provider directory search and filtering
- Knowledge base queries and FAQ retrieval

### 5. **Clean User Experience**
- Professional interface without technical clutter
- User-friendly error messages
- Responsive design for all devices

## 🔍 Usage Examples

### Genie Queries
```python
# Natural language data analysis
genie_client = get_genie_mcp_client()
result = genie_client.query_genie("What are the top 5 claims by amount?")
```

### Unity Catalog Functions
```python
# Member lookup
uc_client = get_uc_functions_mcp_client()
member = uc_client.lookup_member("1001")
claims = uc_client.lookup_claims("1001")
providers = uc_client.lookup_providers("cardiology")
```

### Knowledge Assistant
```python
# Document and FAQ queries
knowledge_client = get_knowledge_assistant_mcp_client(workspace_client)
result = knowledge_client.query_knowledge("What is the prior authorization process?")
```

## 🏗️ Architecture

### MCP Client Architecture

The system implements a modular MCP client architecture:

```python
# Genie MCP Client
class GenieMCPClient:
    def query_genie(self, query: str) -> Dict[str, Any]
    def list_tools(self) -> List[Dict[str, Any]]
    def get_health_status(self) -> Dict[str, Any]

# UC Functions MCP Client
class UCFunctionsMCPClient:
    def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]
    def lookup_member(self, input_id: str) -> Dict[str, Any]
    def lookup_claims(self, member_id: str) -> Dict[str, Any]

# Knowledge Assistant MCP Client
class KnowledgeAssistantMCPClient:
    def query_knowledge(self, query: str) -> Dict[str, Any]
    def get_health_status(self) -> Dict[str, Any]
```

### Databricks Apps Integration

The application is designed to leverage [Databricks Apps](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/) capabilities:

- **Serverless Compute**: Automatic scaling and resource management
- **Integrated Security**: OAuth and service principal authentication
- **Platform Services**: Direct access to Unity Catalog, Model Serving, and Lakeflow Jobs
- **Compliance**: Built-in security and governance features

## 📊 Performance & Monitoring

### Health Check Endpoints
- **Application Health**: `/_stcore/health`
- **MCP Server Status**: Real-time monitoring dashboard
- **Tool Availability**: Automatic health checks

### Performance Optimizations
- **MCP Server Caching**: Optimized data access patterns
- **Connection Pooling**: Efficient resource utilization
- **Error Handling**: Graceful fallbacks and retry logic
- **Auto-scaling**: Leverages Databricks Apps serverless compute

## 🔒 Security

### Authentication & Authorization
- **OAuth Integration**: Required for all MCP connections
- **Workspace-level Permissions**: Enforced through Databricks SDK
- **Service Principal Support**: For automated deployments
- **No Hardcoded Credentials**: Secure token management

### Compliance
- **Unity Catalog Integration**: Governed data access
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: At rest and in transit
- **Network Segmentation**: Isolated compute resources

## 🚨 Troubleshooting

### Common Issues

1. **MCP Connection Failed**
   - Verify Databricks authentication
   - Check workspace hostname and space IDs
   - Ensure proper network access

2. **Configuration Errors**
   - Run `python config.py` to validate configuration
   - Check environment variables for cloud deployment
   - Verify catalog and schema names

3. **Authentication Errors**
   - Run `databricks auth login` to refresh tokens
   - Verify profile name matches configuration
   - Check workspace permissions

### Common Issues & Troubleshooting

#### **Genie Room Issues**
- **"Genie Space not found"**: Verify the Space ID is correct in both `app.yaml` and `config.py`
- **"No data available"**: Ensure `claims_enriched` and `member_claim_summary` tables exist in `payer_gold` schema
- **"Access denied"**: Check that the Genie room has proper permissions for your workspace user
- **"Room not accessible"**: Verify the room is published and not in draft mode

#### **Configuration Issues**
- **"Invalid Space ID"**: Space ID should be a 32-character hexadecimal string (e.g., `01f06a3068a81406a386e8eaefc74545`)
- **"Environment variables not loaded"**: Restart the application after updating `app.yaml`
- **"MCP server unavailable"**: Check workspace connectivity and authentication

#### **Data Issues**
- **"Tables not found"**: Run the medallion ETL notebook first to create the required tables
- **"UDFs not accessible"**: Execute the `02_define_uc_tools_payor.ipynb` notebook
- **"Empty results"**: Verify data is loaded in the Silver/Gold layers

#### **Knowledge Assistant Issues**
- **"Agent Bricks not available"**: Ensure Mosaic AI Agent Bricks Preview (Beta) is enabled
- **"Files not found"**: Verify .txt files are uploaded to Unity Catalog volume in payer_bronze schema
- **"Files too large"**: Files larger than 50 MB are automatically skipped; split large files
- **"Agent creation failed"**: Check serverless compute is enabled and budget policy has nonzero budget
- **"Endpoint not accessible"**: Verify workspace is in supported region and has required permissions
- **"Poor response quality"**: Use "Improve quality" tab to add questions and gather expert feedback
- **"No citations"**: Ensure files are properly uploaded and agent has finished syncing (can take hours)

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

## 📚 Databricks Apps Benefits

Leveraging [Databricks Apps](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/) provides several advantages:

### **Infrastructure Simplification**
- **No Separate Infrastructure**: Apps are hosted on Azure Databricks serverless platform
- **Automatic Scaling**: Built-in resource management and scaling
- **Integrated Services**: Direct access to Unity Catalog, Model Serving, and Lakeflow Jobs

### **Security & Compliance**
- **Built-in Security**: OAuth and service principal authentication
- **Data Governance**: Unity Catalog integration for data access control
- **Compliance Standards**: Support for various compliance profiles

### **Development & Deployment**
- **Local Development**: Develop locally and deploy to workspace
- **Cross-workspace Mobility**: Move apps between workspaces
- **Framework Support**: Python (Streamlit, Dash, Gradio) and Node.js support

### **Operational Benefits**
- **Monitoring & Logging**: Integrated observability tools
- **Resource Limits**: Managed compute resources
- **Network Configuration**: Built-in networking and security controls

## 🚀 Next Steps

1. **Vector Search Integration**: Add vector search MCP server for document analysis
2. **Custom MCP Servers**: Implement custom MCP servers for specific business logic
3. **Multi-agent Architecture**: Extend to multiple specialized agents
4. **Advanced Analytics**: Enhanced reporting and visualization capabilities
5. **Mobile Support**: Responsive design for mobile devices

## 📚 References

- [Databricks Apps Documentation](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/)
- [Databricks Managed MCP Servers](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/mcp/managed-mcp)
- [Agent Bricks: Knowledge Assistant](https://learn.microsoft.com/en-us/azure/databricks/generative-ai/agent-bricks/knowledge-assistant) - Create AI chatbots over documents
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Databricks MCP Python Library](https://pypi.org/project/databricks-mcp/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Databricks First Steps - Payer Medallion Project](https://github.com/bigdatavik/databricksfirststeps) - Initial data setup and medallion architecture

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review Databricks Apps documentation
3. Verify workspace permissions and configuration
4. Test individual MCP client connections
5. Check the application logs for detailed error information

## 📄 License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this project is provided subject to the Databricks License. All included or referenced third party libraries are subject to their respective licenses.

---

## 🏷️ Version Information

- **Current Version**: v2.0.0
- **Python**: 3.11+
- **Streamlit**: 1.50.0+
- **Databricks SDK**: 0.67.0+
- **MCP Integration**: Complete
- **Databricks Apps**: Ready for deployment
