"""
Configuration file for Healthcare Payor AI System
Update these values for your deployment environment
"""

# =============================================================================
# UNITY CATALOG CONFIGURATION
# =============================================================================

# Unity Catalog Configuration
CATALOG_NAME = "my_catalog"  # Update this for your catalog
SCHEMA_NAME = "payer_silver"  # Update this for your schema

# =============================================================================
# DATABRICKS CONFIGURATION
# =============================================================================

# Databricks Profile (for local development)
DATABRICKS_PROFILE = "DEFAULT_azure"  # Update this for your profile

# Workspace Configuration
# Note: In cloud deployment, this is automatically detected by Databricks SDK
# Only needed for local development and MCP server URLs
WORKSPACE_HOSTNAME = "adb-984752964297111.11.azuredatabricks.net"  # Update this for your workspace

# =============================================================================
# GENIE CONFIGURATION
# =============================================================================

# Genie Space ID
GENIE_SPACE_ID = "01f06a3068a81406a386e8eaefc74545"  # Update this for your Genie space

# =============================================================================
# KNOWLEDGE ASSISTANT CONFIGURATION
# =============================================================================

# Knowledge Assistant Endpoint ID
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = "ka-d0808962-endpoint"  # Update this for your Knowledge Assistant endpoint

# =============================================================================
# AI MODEL CONFIGURATION
# =============================================================================

# AI Model Configuration for LLM
AI_MODEL_NAME = "databricks-meta-llama-3-1-8b-instruct"  # Update this for your preferred model

# Alternative models you can use:
# - "databricks-meta-llama-3-1-70b-instruct" (larger, more capable)
# - "databricks-dbrx-instruct" (Databricks optimized model)
# - "databricks-mixtral-8x7b-instruct" (Mixtral model)

# =============================================================================
# CLOUD DEPLOYMENT CONFIGURATION
# =============================================================================

# For cloud deployment, these can be overridden by environment variables
import os

# Override with environment variables if they exist (for cloud deployment)
CATALOG_NAME = os.getenv("CATALOG_NAME", CATALOG_NAME)
SCHEMA_NAME = os.getenv("SCHEMA_NAME", SCHEMA_NAME)
DATABRICKS_PROFILE = os.getenv("DATABRICKS_PROFILE", DATABRICKS_PROFILE)
WORKSPACE_HOSTNAME = os.getenv("WORKSPACE_HOSTNAME", WORKSPACE_HOSTNAME)
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", GENIE_SPACE_ID)
KNOWLEDGE_ASSISTANT_ENDPOINT_ID = os.getenv("KNOWLEDGE_ASSISTANT_ENDPOINT_ID", KNOWLEDGE_ASSISTANT_ENDPOINT_ID)
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", AI_MODEL_NAME)

# In cloud environments, set WORKSPACE_HOSTNAME to auto-detect if not provided
if not WORKSPACE_HOSTNAME or WORKSPACE_HOSTNAME == "":
    WORKSPACE_HOSTNAME = "auto-detect"

# In cloud environments, set DATABRICKS_PROFILE to auto-detect if not provided
if not DATABRICKS_PROFILE or DATABRICKS_PROFILE == "":
    DATABRICKS_PROFILE = "auto-detect"

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config():
    """Validate that all required configuration is set"""
    required_configs = {
        "CATALOG_NAME": CATALOG_NAME,
        "SCHEMA_NAME": SCHEMA_NAME,
        "GENIE_SPACE_ID": GENIE_SPACE_ID,
        "KNOWLEDGE_ASSISTANT_ENDPOINT_ID": KNOWLEDGE_ASSISTANT_ENDPOINT_ID,
        "AI_MODEL_NAME": AI_MODEL_NAME
    }
    
    # WORKSPACE_HOSTNAME and DATABRICKS_PROFILE are optional - can be auto-detected in cloud environments
    if WORKSPACE_HOSTNAME and WORKSPACE_HOSTNAME != "auto-detect":
        required_configs["WORKSPACE_HOSTNAME"] = WORKSPACE_HOSTNAME
    if DATABRICKS_PROFILE and DATABRICKS_PROFILE != "auto-detect":
        required_configs["DATABRICKS_PROFILE"] = DATABRICKS_PROFILE
    
    missing_configs = [key for key, value in required_configs.items() if not value]
    
    if missing_configs:
        raise ValueError(f"Missing required configuration: {', '.join(missing_configs)}")
    
    return True

if __name__ == "__main__":
    validate_config()
    print("✅ Configuration is valid!")
    print(f"Catalog: {CATALOG_NAME}")
    print(f"Schema: {SCHEMA_NAME}")
    print(f"Profile: {DATABRICKS_PROFILE}")
    print(f"Workspace: {WORKSPACE_HOSTNAME}")
    print(f"Genie Space: {GENIE_SPACE_ID}")
    print(f"Knowledge Assistant Endpoint: {KNOWLEDGE_ASSISTANT_ENDPOINT_ID}")
    print(f"AI Model: {AI_MODEL_NAME}")
