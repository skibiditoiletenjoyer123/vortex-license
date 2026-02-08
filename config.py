"""
Configuration file for License System
Edit this file with your settings
"""

import os

class Config:
    """License System Configuration"""
    
    # ==================== SERVER SETTINGS ====================
    
    # License database file
    LICENSES_FILE = "licenses.json"
    
    # Obfuscated mod JAR file (place your jar here)
    OBFUSCATED_MOD_FILE = "obfuscated_mod.jar"
    
    # Server secret key - CHANGE THIS!
    # Use: python -c "import secrets; print(secrets.token_hex(32))"
    SERVER_SECRET = "your-secret-key-change-this"
    
    # Server host and port
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5000
    
    # ==================== CLIENT SETTINGS ====================
    
    # URL of license server (change to your server address)
    SERVER_URL = "http://localhost:5000"
    
    # Command to launch Minecraft with mod
    GAME_LAUNCH_COMMAND = "./gradlew runClient"
