#!/usr/bin/env python3
import requests
import time

def test_server():
    try:
        print("Testing server connection...")
        response = requests.get('http://localhost:8000/health', timeout=10)
        print(f"✅ Server is responding!")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server not running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_server()