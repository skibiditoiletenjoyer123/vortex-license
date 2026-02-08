#!/usr/bin/env python3
"""
Test Vortex License Server Endpoints
Run this to test authentication locally
"""

import requests
import json
import hashlib
import sys

BASE_URL = "http://localhost:5000"

def test_register():
    """Test license registration"""
    print("\n[TEST 1] Register License")
    print("-" * 50)
    
    hwid = "test_hwid_12345678"
    url = f"{BASE_URL}/auth/register"
    
    payload = {"hwid": hwid}
    response = requests.post(url, json=payload)
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json().get('license'), hwid
    return None, None

def test_validate(license_key, hwid):
    """Test license validation (4E compatible endpoint)"""
    print("\n[TEST 2] Validate License")
    print("-" * 50)
    
    url = f"{BASE_URL}/auth/validate"
    
    payload = {
        "hwid": hwid,
        "license_key": license_key,
        "username": "TestPlayer",
        "mode": "login"
    }
    
    response = requests.post(url, json=payload)
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_verify(license_key, hwid):
    """Test license verification"""
    print("\n[TEST 3] Verify License")
    print("-" * 50)
    
    url = f"{BASE_URL}/auth/verify"
    
    payload = {
        "hwid": hwid,
        "license": license_key
    }
    
    response = requests.post(url, json=payload)
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_invalid_license():
    """Test invalid license"""
    print("\n[TEST 4] Invalid License")
    print("-" * 50)
    
    url = f"{BASE_URL}/auth/validate"
    
    payload = {
        "hwid": "unknown_hwid",
        "license_key": "INVALID_KEY",
        "username": "Hacker",
        "mode": "login"
    }
    
    response = requests.post(url, json=payload)
    
    print(f"POST {url}")
    print(f"Request: {json.dumps(payload, indent=2)}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Should be valid=false
    if response.status_code == 200 and not response.json().get('valid'):
        print("✓ Correctly rejected invalid license")
        return True
    return False

def main():
    print("=" * 50)
    print("VORTEX LICENSE SERVER TEST SUITE")
    print("=" * 50)
    
    try:
        # Test 1: Register
        license_key, hwid = test_register()
        if not license_key:
            print("\n❌ Registration failed")
            sys.exit(1)
        
        # Test 2: Validate
        if not test_validate(license_key, hwid):
            print("\n❌ Validation failed")
            sys.exit(1)
        
        # Test 3: Verify
        if not test_verify(license_key, hwid):
            print("\n❌ Verification failed")
            sys.exit(1)
        
        # Test 4: Invalid license
        if not test_invalid_license():
            print("\n❌ Invalid license test failed")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        print("\nServer is ready for deployment!")
        print(f"\nValid license for testing:")
        print(f"  HWID: {hwid}")
        print(f"  License: {license_key}")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print(f"Make sure server is running on {BASE_URL}")
        print("\nTo start server: python license_server_advanced.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
