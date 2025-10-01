# Configuration Guide

This guide explains how to configure the Healthcare Payor AI System for different deployment environments.

## Configuration Files

### 1. `config.py` - Main Configuration File

This is the central configuration file that contains all the settings for your deployment.

```python
# Unity Catalog Configuration
CATALOG_NAME = "my_catalog"  # Update this for your catalog
SCHEMA_NAME = "payer_silver"  # Update this for your schema

# Databricks Configuration
DATABRICKS_PROFILE = "DEFAULT_azure"  # Update this for your profile
WORKSPACE_HOSTNAME = "adb-984752964297111.11.azuredatabricks.net"  # Update this for your workspace

# Genie Configuration
GENIE_SPACE_ID = "01f06a3068a81406a386e8eaefc74545"  # Update this for your Genie space
```

### 2. `app.yaml.example` - Cloud Deployment Template

Copy this file to `app.yaml` and update the environment variables for cloud deployment.

## Configuration Methods

### Local Development

1. **Edit `config.py`** directly with your values
2. **Run the app** - it will use the values from `config.py`

### Cloud Deployment

1. **Copy `app.yaml.example` to `app.yaml`**
2. **Update the environment variables** in `app.yaml` with your values
3. **Deploy** - the app will read from environment variables

## Required Configuration Values

| Variable | Description | Example |
|----------|-------------|---------|
| `CATALOG_NAME` | Unity Catalog name | `my_catalog` |
| `SCHEMA_NAME` | Schema name containing UC functions | `payer_silver` |
| `DATABRICKS_PROFILE` | Databricks CLI profile | `DEFAULT_azure` |
| `WORKSPACE_HOSTNAME` | Databricks workspace hostname | `adb-123456789.11.azuredatabricks.net` |
| `GENIE_SPACE_ID` | Genie space ID | `01f06a3068a81406a386e8eaefc74545` |

## Environment Variable Override

The configuration system supports environment variable override for cloud deployment:

```bash
# Set environment variables
export CATALOG_NAME="your_catalog"
export SCHEMA_NAME="your_schema"
export DATABRICKS_PROFILE="your_profile"
export WORKSPACE_HOSTNAME="your-workspace.azuredatabricks.net"
export GENIE_SPACE_ID="your_genie_space_id"
```

## Validation

The configuration system includes validation to ensure all required values are set:

```python
from config import validate_config
validate_config()  # Raises ValueError if any required config is missing
```

## Testing Configuration

You can test your configuration by running:

```bash
python config.py
```

This will validate the configuration and print the current values.

## Troubleshooting

### Common Issues

1. **ImportError**: If you get import errors, check that all required packages are installed
2. **Missing Configuration**: Ensure all required environment variables are set
3. **Invalid Values**: Verify that your catalog, schema, and workspace values are correct

### Fallback Values

If the configuration import fails, the system will fall back to default values defined in each MCP client file.
