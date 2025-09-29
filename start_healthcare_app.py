#!/usr/bin/env python3
"""
Healthcare Payor AI System Startup Script
Configurable startup script for the Healthcare Payor AI System
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Start Healthcare Payor AI System')
    
    # Environment configuration
    parser.add_argument('--conda-env', default='azure_databricks',
                       help='Conda environment name (default: azure_databricks)')
    
    # Databricks configuration
    parser.add_argument('--catalog', default='my_catalog',
                       help='Unity Catalog name (default: my_catalog)')
    parser.add_argument('--schema', default='payer_silver',
                       help='Schema name (default: payer_silver)')
    parser.add_argument('--databricks-profile', default='DEFAULT',
                       help='Databricks CLI profile (default: DEFAULT)')
    
    # LLM configuration
    parser.add_argument('--llm-endpoint', default='databricks-meta-llama-3-3-70b-instruct',
                       help='LLM endpoint name (default: databricks-meta-llama-3-3-70b-instruct)')
    parser.add_argument('--llm-temperature', type=float, default=0.1,
                       help='LLM temperature (default: 0.1)')
    
    
    # Streamlit configuration
    parser.add_argument('--port', type=int, default=8501,
                       help='Streamlit port (default: 8501)')
    parser.add_argument('--host', default='localhost',
                       help='Streamlit host (default: localhost)')
    parser.add_argument('--enhanced', action='store_true',
                       help='Use enhanced version with analytics and workflows')
    
    # Debug options
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--test-connection', action='store_true',
                       help='Test connections before starting app')
    
    return parser.parse_args()

def detect_databricks_profile():
    """Automatically detect the best Databricks profile to use"""
    try:
        # Try to read the databricks config file
        config_path = os.path.expanduser("~/.databrickscfg")
        if not os.path.exists(config_path):
            print("❌ No Databricks configuration found")
            return None
        
        # Parse the config file to find profiles with tokens
        profiles_with_tokens = []
        current_profile = None
        
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    current_profile = line[1:-1]
                elif line.startswith('token') and current_profile:
                    profiles_with_tokens.append(current_profile)
        
        # Prefer DEFAULT_azure, then any profile with token, then DEFAULT
        preferred_order = ['DEFAULT_azure', 'DEFAULT']
        for preferred in preferred_order:
            if preferred in profiles_with_tokens:
                return preferred
        
        # If no preferred profile found, use the first one with a token
        if profiles_with_tokens:
            return profiles_with_tokens[0]
        
        return 'DEFAULT'
        
    except Exception as e:
        print(f"⚠️  Could not auto-detect Databricks profile: {e}")
        return 'DEFAULT'

def set_environment_variables(args):
    """Set environment variables for the app"""
    env_vars = {
        'HEALTHCARE_CATALOG': args.catalog,
        'HEALTHCARE_SCHEMA': args.schema,
        'HEALTHCARE_LLM_ENDPOINT': args.llm_endpoint,
        'HEALTHCARE_LLM_TEMPERATURE': str(args.llm_temperature),
        'HEALTHCARE_DEBUG': str(args.debug).lower()
    }
    
    # Auto-detect Databricks profile if not specified
    if args.databricks_profile == 'DEFAULT':
        detected_profile = detect_databricks_profile()
        if detected_profile and detected_profile != 'DEFAULT':
            print(f"🔍 Auto-detected Databricks profile: {detected_profile}")
            args.databricks_profile = detected_profile
    
    # Set Databricks profile environment variable
    env_vars['DATABRICKS_CONFIG_PROFILE'] = args.databricks_profile
    env_vars['HEALTHCARE_DATABRICKS_PROFILE'] = args.databricks_profile
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ Set {key}={value}")

def test_connections(args):
    """Test Databricks and conda environment connections"""
    print("🔍 Testing connections...")
    
    # Test conda environment
    try:
        result = subprocess.run(['conda', 'info', '--envs'], 
                              capture_output=True, text=True, check=True)
        if args.conda_env not in result.stdout:
            print(f"❌ Conda environment '{args.conda_env}' not found")
            return False
        print(f"✅ Conda environment '{args.conda_env}' found")
    except subprocess.CalledProcessError:
        print("❌ Conda not available")
        return False
    
    # Test Databricks CLI
    try:
        # Use the detected profile for testing
        env = os.environ.copy()
        env['DATABRICKS_CONFIG_PROFILE'] = args.databricks_profile
        
        result = subprocess.run(['databricks', 'workspace', 'list', '/'], 
                              capture_output=True, text=True, check=True, env=env)
        print("✅ Databricks CLI connection successful")
    except subprocess.CalledProcessError as e:
        print("❌ Databricks CLI connection failed")
        print(f"Error: {e}")
        print("Please configure Databricks CLI with: databricks configure")
        return False
    
    # Test required packages
    try:
        result = subprocess.run([
            'conda', 'run', '-n', args.conda_env, 'python', '-c',
            'import databricks_langchain, unitycatalog_langchain, langchain'
        ], capture_output=True, text=True, check=True)
        print("✅ Required packages available")
    except subprocess.CalledProcessError:
        print("❌ Required packages not available")
        print(f"Installing packages in {args.conda_env}...")
        try:
            subprocess.run([
                'conda', 'run', '-n', args.conda_env, 'pip', 'install',
                'databricks-langchain', 'unitycatalog-langchain[databricks]', 
                'langchain', 'langchain-core', 'streamlit'
            ], check=True)
            print("✅ Packages installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            return False
    
    return True

def create_config_file(args):
    """Create a configuration file for the app"""
    config_content = f"""# Healthcare Payor AI System Configuration
# Generated by start_healthcare_app.py

# Databricks Configuration
CATALOG = "{args.catalog}"
SCHEMA = "{args.schema}"
DATABRICKS_PROFILE = "{args.databricks_profile}"

# LLM Configuration
LLM_ENDPOINT = "{args.llm_endpoint}"
LLM_TEMPERATURE = {args.llm_temperature}

# Debug Configuration
DEBUG = {str(args.debug).lower()}
"""
    
    config_path = Path(__file__).parent / "app_config.py"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created configuration file: {config_path}")

def start_streamlit_app(args):
    """Start the Streamlit app"""
    # Choose app version based on enhanced flag
    if args.enhanced:
        app_path = Path(__file__).parent / "enhanced_healthcare_payor_app.py"
        app_name = "Enhanced Healthcare Payor AI System"
    else:
        app_path = Path(__file__).parent / "healthcare_payor_streamlit_app.py"
        app_name = "Healthcare Payor AI System"
    
    if not app_path.exists():
        print(f"❌ App file not found: {app_path}")
        return False
    
    # Build the conda run command
    cmd = [
        'conda', 'run', '-n', args.conda_env,
        'streamlit', 'run', str(app_path),
        '--server.port', str(args.port),
        '--server.address', args.host
    ]
    
    if args.debug:
        cmd.extend(['--logger.level', 'debug'])
    
    print(f"🚀 Starting {app_name}...")
    print(f"📱 App will be available at: http://{args.host}:{args.port}")
    print(f"🔧 Configuration:")
    print(f"   - App Version: {'Enhanced' if args.enhanced else 'Standard'}")
    print(f"   - Conda Environment: {args.conda_env}")
    print(f"   - Databricks Profile: {args.databricks_profile}")
    print(f"   - Catalog: {args.catalog}")
    print(f"   - Schema: {args.schema}")
    print(f"   - LLM Endpoint: {args.llm_endpoint}")
    print(f"   - Debug Mode: {args.debug}")
    
    try:
        # Set environment variables for the subprocess
        env = os.environ.copy()
        env['DATABRICKS_CONFIG_PROFILE'] = args.databricks_profile
        subprocess.run(cmd, check=True, env=env)
    except KeyboardInterrupt:
        print("\n🛑 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🏥 Healthcare Payor AI System Startup Script")
    print("=" * 50)
    
    # Parse arguments
    args = parse_arguments()
    
    # Set environment variables
    set_environment_variables(args)
    
    # Create configuration file
    create_config_file(args)
    
    # Test connections if requested
    if args.test_connection:
        if not test_connections(args):
            print("❌ Connection tests failed")
            sys.exit(1)
        print("✅ All connection tests passed")
    
    # Start the app
    if not start_streamlit_app(args):
        sys.exit(1)

if __name__ == "__main__":
    main()
