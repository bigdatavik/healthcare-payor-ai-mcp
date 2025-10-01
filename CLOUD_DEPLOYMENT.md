# Healthcare Payor AI System - MCP Cloud Deployment Guide

## 🚀 Quick Cloud Deployment

This guide provides instructions for deploying the Healthcare Payor AI System with MCP integration to various cloud platforms.

### Prerequisites
- Python 3.11+
- Git
- Cloud platform account (AWS/Azure/GCP)
- Databricks workspace access

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/bigdatavik/hospital-ai-system.git
cd hospital-ai-system
git checkout deployment-clean
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Set Databricks profile
export DATABRICKS_PROFILE="DEFAULT_azure"

# Set OpenAI API key (for Knowledge Assistant)
export OPENAI_API_KEY="your-openai-api-key"
```

## ☁️ Cloud Platform Deployments

### AWS Deployment

#### Option 1: AWS App Runner
```yaml
# apprunner.yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  runtime-version: 3.11
  command: streamlit run enhanced_healthcare_payor_app.py --server.port 8080 --server.address 0.0.0.0
  network:
    port: 8080
    env: PORT
```

#### Option 2: AWS Elastic Beanstalk
```yaml
# .ebextensions/streamlit.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: enhanced_healthcare_payor_app.py
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: static
```

#### Option 3: AWS ECS with Fargate
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "enhanced_healthcare_payor_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Azure Deployment

#### Option 1: Azure Container Instances
```yaml
# azure-deploy.yml
apiVersion: 2019-12-01
location: eastus
name: healthcare-payor-ai
properties:
  containers:
  - name: healthcare-payor-ai
    properties:
      image: your-registry.azurecr.io/healthcare-payor-ai:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
      ports:
      - port: 8501
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8501
```

#### Option 2: Azure App Service
```bash
# Deploy to Azure App Service
az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name healthcare-payor-ai --runtime "PYTHON|3.11"
az webapp config appsettings set --resource-group myResourceGroup --name healthcare-payor-ai --settings DATABRICKS_PROFILE="DEFAULT_azure"
```

### Google Cloud Platform

#### Option 1: Cloud Run
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/healthcare-payor-ai', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/healthcare-payor-ai']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'healthcare-payor-ai', '--image', 'gcr.io/$PROJECT_ID/healthcare-payor-ai', '--platform', 'managed', '--region', 'us-central1', '--allow-unauthenticated']
```

#### Option 2: App Engine
```yaml
# app.yaml
runtime: python311
service: healthcare-payor-ai

env_variables:
  DATABRICKS_PROFILE: "DEFAULT_azure"
  OPENAI_API_KEY: "your-openai-api-key"

handlers:
- url: /.*
  script: auto
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "enhanced_healthcare_payor_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  healthcare-payor-ai:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DATABRICKS_PROFILE=DEFAULT_azure
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 🔧 Environment Variables

### Required
```bash
DATABRICKS_PROFILE=DEFAULT_azure
OPENAI_API_KEY=your-openai-api-key
```

### Optional
```bash
# Streamlit configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Databricks configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token

# Application configuration
HEALTHCARE_CATALOG=my_catalog
HEALTHCARE_SCHEMA=payer_silver
HEALTHCARE_LLM_ENDPOINT=databricks-meta-llama-3-3-70b-instruct
```

## 📊 Monitoring & Logging

### Health Check Endpoint
The application provides a health check endpoint at `/_stcore/health`

### Logging Configuration
```python
# Add to enhanced_healthcare_payor_app.py
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🚀 Production Considerations

### Performance Optimization
- Use `mlflow-skinny` instead of full MLflow for smaller footprint
- Enable gzip compression
- Use CDN for static assets
- Implement caching for frequently accessed data

### Security
- Use environment variables for sensitive data
- Implement proper authentication
- Enable HTTPS
- Regular security updates

### Scaling
- Use load balancers for multiple instances
- Implement horizontal pod autoscaling
- Monitor resource usage
- Set up auto-scaling policies

## 📝 Troubleshooting

### Common Issues
1. **Port binding errors**: Ensure port 8501 is available
2. **Memory issues**: Increase container memory limits
3. **Databricks connection**: Verify credentials and network access
4. **OpenAI API**: Check API key and rate limits

### Debug Mode
```bash
# Run with debug logging
STREAMLIT_LOGGER_LEVEL=debug streamlit run enhanced_healthcare_payor_app.py
```

## 📞 Support

For deployment issues:
- Check the logs: `docker logs <container-name>`
- Verify environment variables
- Test Databricks connectivity
- Review Streamlit documentation

## 🏷️ Version Information

- **Current Version**: `all-working-sep30-9-40am`
- **Python**: 3.11+
- **Streamlit**: 1.50.0+
- **Databricks SDK**: 0.67.0+
