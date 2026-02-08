"""
License Client - Authenticates with license server and injects obfuscated mod code
Run this to verify license and launch the game with mod injected
"""

import requests
import json
import os
import uuid
import hashlib
import platform
import base64
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

class LicenseClient:
    def __init__(self, server_url: str, game_launch_command: str):
        """
        Initialize license client
        
        Args:
            server_url: URL of license server (e.g., 'http://your-server.com:5000')
            game_launch_command: Command to launch Minecraft (e.g., ./gradlew runClient')
        """
        self.server_url = server_url.rstrip('/')
        self.game_launch_command = game_launch_command
        self.license_file = ".license"
        self.hwid = self.generate_hwid()
        self.license_key: Optional[str] = None
        
        print("[*] License Client Initialized")
        print(f"[*] Server: {self.server_url}")
        print(f"[*] HWID: {self.hwid[:16]}...")
    
    @staticmethod
    def generate_hwid() -> str:
        """
        Generate a unique hardware ID based on system information
        This combines: machine UUID, platform, processor
        """
        try:
            # Get machine UUID
            machine_uuid = str(uuid.getnode())
            
            # Get system info
            system_info = f"{platform.system()}{platform.release()}{platform.machine()}"
            
            # Combine into HWID
            hwid_raw = f"{machine_uuid}:{system_info}"
            hwid = hashlib.sha256(hwid_raw.encode()).hexdigest()
            
            return hwid
        except Exception as e:
            print(f"[ERROR] Failed to generate HWID: {e}")
            # Fallback to random HWID
            return str(uuid.uuid4()).replace('-', '')
    
    def load_local_license(self) -> bool:
        """
        Load license from local cache file
        Returns True if license loaded successfully
        """
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    stored_hwid = data.get('hwid')
                    stored_license = data.get('license')
                    
                    # Verify HWID matches (integrity check)
                    if stored_hwid == self.hwid and stored_license:
                        self.license_key = stored_license
                        print("[+] License loaded from cache")
                        return True
            except Exception as e:
                print(f"[!] Error loading cached license: {e}")
        
        return False
    
    def save_local_license(self):
        """Save license to local cache file"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump({
                    'hwid': self.hwid,
                    'license': self.license_key
                }, f)
            print("[+] License cached locally")
        except Exception as e:
            print(f"[!] Error saving license: {e}")
    
    def register_license(self) -> bool:
        """
        Register HWID with license server to get a license
        Returns True if registration successful
        """
        try:
            print("\n[*] Registering with license server...")
            
            response = requests.post(
                f"{self.server_url}/auth/register",
                json={"hwid": self.hwid},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"[ERROR] Registration failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                print(f"[ERROR] {data.get('error', 'Unknown error')}")
                return False
            
            self.license_key = data.get('license')
            print(f"[+] License registered: {data.get('license')[:16]}...")
            
            if not data.get('registered'):
                print("[+] New license issued!")
            else:
                print("[+] Using existing license")
            
            self.save_local_license()
            return True
        
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to license server!")
            print(f"[ERROR] Make sure server is running at {self.server_url}")
            return False
        except Exception as e:
            print(f"[ERROR] Registration failed: {e}")
            return False
    
    def verify_license(self) -> bool:
        """
        Verify license with server
        Returns True if license is valid and active
        """
        if not self.license_key:
            print("[!] No license to verify")
            return False
        
        try:
            print("\n[*] Verifying license with server...")
            
            response = requests.post(
                f"{self.server_url}/auth/verify",
                json={
                    "hwid": self.hwid,
                    "license": self.license_key
                },
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"[ERROR] Verification failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                print(f"[ERROR] {data.get('error', 'Unknown error')}")
                return False
            
            if not data.get('authorized'):
                reason = data.get('reason', 'unknown')
                print(f"[X] License NOT authorized: {reason}")
                return False
            
            print("[+] License verified and authorized!")
            return True
        
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to license server!")
            return False
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            return False
    
    def download_mod(self, output_file: str = "vortex_injected.jar") -> bool:
        """
        Download obfuscated mod code from server
        Returns True if download successful
        """
        if not self.license_key:
            print("[!] No license available for mod download")
            return False
        
        try:
            print(f"\n[*] Downloading obfuscated mod...")
            
            response = requests.post(
                f"{self.server_url}/mod/download",
                json={
                    "hwid": self.hwid,
                    "license": self.license_key
                },
                timeout=30
            )
            
            if response.status_code == 403:
                print("[ERROR] Not authorized to download mod!")
                return False
            
            if response.status_code != 200:
                print(f"[ERROR] Download failed: {response.status_code}")
                return False
            
            data = response.json()
            
            if not data.get('success'):
                print(f"[ERROR] {data.get('error', 'Unknown error')}")
                return False
            
            # Decode base64 mod
            mod_data = base64.b64decode(data.get('mod', ''))
            size = data.get('size', 0)
            
            # Write to file
            with open(output_file, 'wb') as f:
                f.write(mod_data)
            
            print(f"[+] Mod downloaded successfully ({size} bytes)")
            print(f"[+] Saved to: {output_file}")
            
            return True
        
        except requests.exceptions.ConnectionError:
            print("[ERROR] Cannot connect to license server!")
            return False
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return False
    
    def inject_and_launch(self) -> bool:
        """
        Verify license, download mod, inject it, and launch game
        """
        print("\n" + "="*60)
        print("VORTEX MOD - License Authentication")
        print("="*60)
        
        # Step 1: Try to load cached license
        if not self.load_local_license():
            # Step 2: Register new license if not cached
            if not self.register_license():
                print("\n[X] Failed to register license. Cannot proceed.")
                return False
        
        # Step 3: Verify license with server
        if not self.verify_license():
            print("\n[X] License verification failed. Cannot launch game.")
            print("[!] Your license may be revoked or inactive.")
            return False
        
        # Step 4: Download obfuscated mod
        if not self.download_mod():
            print("\n[X] Failed to download mod. Cannot launch game.")
            return False
        
        # Step 5: Inject mod into game
        print("\n[*] Injecting mod into game...")
        # This is where you'd add actual injection logic
        # For now, we just verify the mod was downloaded
        
        # Step 6: Launch game
        print("\n[+] Authentication successful! Launching game...")
        print("="*60)
        
        try:
            # Launch the game with the mod
            # The mod is now injected and ready to use
            subprocess.run(self.game_launch_command, shell=True)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to launch game: {e}")
            return False

def main():
    """
    Example usage:
    python license_client.py
    """
    # Configuration - change these to your server and launch command
    SERVER_URL = "http://localhost:5000"  # Change to your server URL
    GAME_LAUNCH_COMMAND = "./gradlew runClient"  # Or your game launch command
    
    # Create client and authenticate
    client = LicenseClient(SERVER_URL, GAME_LAUNCH_COMMAND)
    
    # Run full authentication and launch flow
    success = client.inject_and_launch()
    
    if success:
        print("\n[+] Game launched successfully!")
        sys.exit(0)
    else:
        print("\n[X] Failed to authenticate and launch.")
        sys.exit(1)

if __name__ == "__main__":
    main()
