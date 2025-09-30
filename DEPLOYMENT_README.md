# Healthcare Payor AI System - Clean Deployment

## 🚀 Quick Start

This is a clean deployment version with only the essential files needed to run the Healthcare Payor AI System.

### Prerequisites
- Python 3.11
- Conda environment: `azure_databricks_py311`
- Databricks profile: `DEFAULT_azure`

### Installation

1. **Activate the conda environment:**
   ```bash
   conda activate azure_databricks_py311
   ```

2. **Install dependencies:**
   ```bash
   pip install -r app_requirements.txt
   ```

3. **Start the application:**
   ```bash
   ./start_app.sh
   ```

### Access the App
- **Local URL**: http://localhost:8502
- **Network URL**: http://10.248.121.198:8502

## 📁 Essential Files

### Core Application Files
- `enhanced_healthcare_payor_app.py` - Main Streamlit application
- `genie_multiagent_tool.py` - Genie integration tool
- `langgraph_genie_multiagent.py` - Multi-agent system
- `unstructured_data_processor.py` - Data processing utilities

### Configuration Files
- `app_requirements.txt` - Python dependencies
- `requirements_complete_frozen.txt` - Complete frozen environment
- `requirements_frozen.txt` - Basic frozen requirements
- `databricks.yml` - Databricks configuration

### Data & Resources
- `data/` - Knowledge base and sample data
- `notebooks/` - Jupyter notebooks for development

### Scripts
- `start_app.sh` - Application startup script

## 🔧 Features

- **UC Functions**: Member lookup, claims lookup, provider lookup
- **Genie Query**: Natural language data querying
- **Knowledge Assistant**: Document analysis and Q&A
- **Multi-agent System**: Coordinated AI agents for complex tasks

## 🏷️ Version

Tag: `all-working-sep30-9-40am`
- UC client configuration fixed
- All 5 tools working properly
- Streamlit app running successfully

## 📝 Notes

This deployment branch contains only the essential files needed to run the application, making it ideal for production deployment and avoiding confusion with duplicate files.
