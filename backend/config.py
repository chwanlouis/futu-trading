"""
Configuration module for Futu Agent
Handles connection settings and other configurations
"""

import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Futu Agent"""

    # FutuOpenD Connection Settings
    FUTU_HOST = os.getenv("FUTU_HOST", "127.0.0.1")
    FUTU_PORT = int(os.getenv("FUTU_PORT", 11111))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Trading Settings
    DEFAULT_MARKET = os.getenv("DEFAULT_MARKET", "HK")
    ORDER_TIMEOUT = int(os.getenv("ORDER_TIMEOUT", 30))  # seconds

    # API Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", 1))  # seconds

    @classmethod
    def get_futu_connection_params(cls) -> dict:
        """Get FutuOpenD connection parameters"""
        return {
            "host": cls.FUTU_HOST,
            "port": cls.FUTU_PORT,
        }

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development") == "production"

    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("=== Futu Agent Configuration ===")
        print(f"Host: {cls.FUTU_HOST}")
        print(f"Port: {cls.FUTU_PORT}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Default Market: {cls.DEFAULT_MARKET}")
        print(f"Order Timeout: {cls.ORDER_TIMEOUT}s")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"Retry Delay: {cls.RETRY_DELAY}s")
        print(f"Production: {cls.is_production()}")
