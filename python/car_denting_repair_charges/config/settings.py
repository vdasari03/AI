import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    

class DevelopmentConfig(Config):
    """Development configuration"""
    USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "True").lower() == "true"
    MOCK_RESPONSES_PATH = os.path.join(os.path.dirname(__file__), "..", "tests", "mocks", "responses.json")


class ProductionConfig(Config):
    """Production configuration"""
    USE_MOCK_LLM = False
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-vision-preview")


class TestConfig(Config):
    """Test configuration"""
    USE_MOCK_LLM = True
    TESTING = True
    MOCK_RESPONSES_PATH = os.path.join(os.path.dirname(__file__), "..", "tests", "mocks", "responses.json")


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionConfig
    elif env == "test":
        return TestConfig
    else:
        return DevelopmentConfig
