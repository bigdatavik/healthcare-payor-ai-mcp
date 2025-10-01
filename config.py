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
WORKSPACE_HOSTNAME = "adb-984752964297111.11.azuredatabricks.net"  # Update this for your workspace

# =============================================================================
# GENIE CONFIGURATION
# =============================================================================

# Genie Space ID
GENIE_SPACE_ID = "01f06a3068a81406a386e8eaefc74545"  # Update this for your Genie space

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

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config():
    """Validate that all required configuration is set"""
    required_configs = {
        "CATALOG_NAME": CATALOG_NAME,
        "SCHEMA_NAME": SCHEMA_NAME,
        "DATABRICKS_PROFILE": DATABRICKS_PROFILE,
        "WORKSPACE_HOSTNAME": WORKSPACE_HOSTNAME,
        "GENIE_SPACE_ID": GENIE_SPACE_ID
    }
    
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
