"""
Configuration Management for LifeAI Emergency Assistant
Loads environment variables and provides centralized configuration access
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

class Config:
    """Centralized configuration management"""
    
    # ===================================================================
    # AWS CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_aws_config():
        """Get AWS configuration"""
        return {
            'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            'session_token': os.getenv('AWS_SESSION_TOKEN')
        }
    
    # ===================================================================
    # S3 CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_s3_config():
        """Get S3 configuration"""
        return {
            'bucket_name': os.getenv('S3_BUCKET_NAME', 'emergency-protocols-bucket'),
            'audio_bucket': os.getenv('S3_AUDIO_BUCKET', 'emergency-audio-bucket'),
            'region': os.getenv('S3_REGION', 'us-east-1')
        }
    
    # ===================================================================
    # DYNAMODB CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_dynamodb_config():
        """Get DynamoDB configuration"""
        return {
            'table_name': os.getenv('DYNAMODB_TABLE_NAME', 'EmergencyIncidents'),
            'region': os.getenv('DYNAMODB_REGION', 'us-east-1')
        }
    
    # ===================================================================
    # BEDROCK CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_bedrock_config():
        """Get Amazon Bedrock configuration"""
        return {
            'region': os.getenv('BEDROCK_REGION', 'us-east-1'),
            'model_id': os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
            'fallback_model': os.getenv('BEDROCK_FALLBACK_MODEL', 'anthropic.claude-3-haiku-20240307-v1:0')
        }
    
    # ===================================================================
    # TRANSCRIBE CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_transcribe_config():
        """Get Amazon Transcribe configuration"""
        return {
            'region': os.getenv('TRANSCRIBE_REGION', 'us-east-1'),
            'language_code': os.getenv('TRANSCRIBE_LANGUAGE_CODE', 'en-US')
        }
    
    # ===================================================================
    # APPLICATION CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_app_config():
        """Get application configuration"""
        return {
            'name': os.getenv('APP_NAME', 'LifeAI Emergency Assistant'),
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'debug_mode': os.getenv('DEBUG_MODE', 'True').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'environment': os.getenv('ENVIRONMENT', 'development')
        }
    
    # ===================================================================
    # EMERGENCY SETTINGS
    # ===================================================================
    
    @staticmethod
    def get_emergency_config():
        """Get emergency response configuration"""
        return {
            'timeout': int(os.getenv('DEFAULT_EMERGENCY_TIMEOUT', '30')),
            'max_retries': int(os.getenv('MAX_RETRY_ATTEMPTS', '3')),
            'emergency_contact': os.getenv('EMERGENCY_CONTACT_PHONE', '+1234567890'),
            'simulate_calls': os.getenv('SIMULATE_EMERGENCY_CALLS', 'True').lower() == 'true'
        }
    
    # ===================================================================
    # SECURITY CONFIGURATION
    # ===================================================================
    
    @staticmethod
    def get_security_config():
        """Get security configuration"""
        return {
            'encryption_key': os.getenv('ENCRYPTION_KEY'),
            'jwt_secret': os.getenv('JWT_SECRET')
        }
    
    # ===================================================================
    # EXTERNAL SERVICES
    # ===================================================================
    
    @staticmethod
    def get_external_services_config():
        """Get external services configuration"""
        return {
            'google_maps_key': os.getenv('GOOGLE_MAPS_API_KEY'),
            'twilio_sid': os.getenv('TWILIO_ACCOUNT_SID'),
            'twilio_token': os.getenv('TWILIO_AUTH_TOKEN'),
            'weather_api_key': os.getenv('WEATHER_API_KEY')
        }
    
    # ===================================================================
    # STREAMLIT SECRETS FALLBACK
    # ===================================================================
    
    @staticmethod
    def get_streamlit_secrets():
        """Get configuration from Streamlit secrets as fallback"""
        try:
            return {
                's3_bucket': st.secrets.get("S3_BUCKET_NAME"),
                'dynamodb_table': st.secrets.get("DYNAMODB_TABLE_NAME"),
                'aws_region': st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
            }
        except:
            return {}
    
    # ===================================================================
    # VALIDATION METHODS
    # ===================================================================
    
    @staticmethod
    def validate_aws_config():
        """Validate AWS configuration"""
        aws_config = Config.get_aws_config()
        
        required_fields = ['region']
        missing_fields = []
        
        for field in required_fields:
            if not aws_config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            st.warning(f"Missing AWS configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @staticmethod
    def validate_s3_config():
        """Validate S3 configuration"""
        s3_config = Config.get_s3_config()
        
        if not s3_config.get('bucket_name') or s3_config['bucket_name'] == 'emergency-protocols-bucket':
            st.warning("⚠️ Please update S3_BUCKET_NAME in .env file")
            return False
        
        return True
    
    @staticmethod
    def validate_all_config():
        """Validate all configuration"""
        validations = [
            Config.validate_aws_config(),
            Config.validate_s3_config()
        ]
        
        return all(validations)

# ===================================================================
# CONFIGURATION INSTANCES
# ===================================================================

# Create global configuration instances
AWS_CONFIG = Config.get_aws_config()
S3_CONFIG = Config.get_s3_config()
DYNAMODB_CONFIG = Config.get_dynamodb_config()
BEDROCK_CONFIG = Config.get_bedrock_config()
APP_CONFIG = Config.get_app_config()
EMERGENCY_CONFIG = Config.get_emergency_config()

# ===================================================================
# HELPER FUNCTIONS
# ===================================================================

def get_bucket_name():
    """Get S3 bucket name with fallback"""
    return S3_CONFIG['bucket_name']

def get_table_name():
    """Get DynamoDB table name with fallback"""
    return DYNAMODB_CONFIG['table_name']

def get_aws_region():
    """Get AWS region with fallback"""
    return AWS_CONFIG['region']

def get_bedrock_model():
    """Get Bedrock model ID with fallback"""
    return BEDROCK_CONFIG['model_id']

def is_debug_mode():
    """Check if debug mode is enabled"""
    return APP_CONFIG['debug_mode']

def is_production():
    """Check if running in production"""
    return APP_CONFIG['environment'] == 'production'

# ===================================================================
# CONFIGURATION DISPLAY (for debugging)
# ===================================================================

def display_config_status():
    """Display configuration status in Streamlit sidebar"""
    
    with st.sidebar:
        st.markdown("### 🔧 Configuration Status")
        
        # AWS Configuration
        if Config.validate_aws_config():
            st.success("✅ AWS Config")
        else:
            st.error("❌ AWS Config")
        
        # S3 Configuration
        if Config.validate_s3_config():
            st.success("✅ S3 Config")
        else:
            st.error("❌ S3 Config")
        
        # Display current settings (non-sensitive)
        st.markdown("**Current Settings:**")
        st.text(f"Region: {get_aws_region()}")
        st.text(f"Environment: {APP_CONFIG['environment']}")
        st.text(f"Debug: {is_debug_mode()}")
        
        if is_debug_mode():
            st.markdown("**Debug Info:**")
            st.text(f"Bucket: {get_bucket_name()}")
            st.text(f"Table: {get_table_name()}")
            st.text(f"Model: {get_bedrock_model()}")

# ===================================================================
# EXPORT ALL CONFIGURATIONS
# ===================================================================

__all__ = [
    'Config',
    'AWS_CONFIG',
    'S3_CONFIG', 
    'DYNAMODB_CONFIG',
    'BEDROCK_CONFIG',
    'APP_CONFIG',
    'EMERGENCY_CONFIG',
    'get_bucket_name',
    'get_table_name',
    'get_aws_region',
    'get_bedrock_model',
    'is_debug_mode',
    'is_production',
    'display_config_status'
]