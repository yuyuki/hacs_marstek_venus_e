"""Test script to check available data from Marstek device."""
import socket
import json
import sys
import time

def send_request(sock, ip, port, method, params=None):
    """Send JSON-RPC request and return response."""
    request = {
        "id": 0,
        "method": method,
    }
    if params:
        request["params"] = params
    
    try:
        sock.sendto(json.dumps(request).encode("utf-8"), (ip, port))
        print(f"\n→ Sent {method} request")
        
        sock.settimeout(5.0)
        data, addr = sock.recvfrom(4096)
        response = json.loads(data.decode("utf-8"))
        print(f"← Received response")
        return response
    except socket.timeout:
        print(f"✗ Timeout waiting for {method}")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_available_data.py <device_ip>")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = 30000
    
    print(f"Testing Marstek Venus E at {ip}:{port}")
    print("=" * 60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Test ES.GetStatus
        print("\n1. ES.GetStatus - Energy System Status")
        print("-" * 60)
        response = send_request(sock, ip, port, "ES.GetStatus", {"id": 0})
        if response and "result" in response:
            result = response["result"]
            print(json.dumps(result, indent=2))
            available_fields = list(result.keys())
            print(f"\nAvailable fields: {', '.join(available_fields)}")
        
        time.sleep(1)
        
        # Test Bat.GetStatus
        print("\n2. Bat.GetStatus - Battery Status")
        print("-" * 60)
        response = send_request(sock, ip, port, "Bat.GetStatus", {"id": 0})
        if response and "result" in response:
            result = response["result"]
            print(json.dumps(result, indent=2))
            available_fields = list(result.keys())
            print(f"\nAvailable fields: {', '.join(available_fields)}")
        
        time.sleep(1)
        
        # Test ES.GetMode
        print("\n3. ES.GetMode - Current Mode")
        print("-" * 60)
        response = send_request(sock, ip, port, "ES.GetMode", {"id": 0})
        if response and "result" in response:
            result = response["result"]
            print(json.dumps(result, indent=2))
            available_fields = list(result.keys())
            print(f"\nAvailable fields: {', '.join(available_fields)}")
        
        time.sleep(1)
        
        # Test Marstek.GetDevice
        print("\n4. Marstek.GetDevice - Device Info")
        print("-" * 60)
        response = send_request(sock, ip, port, "Marstek.GetDevice", {"ble_mac": "0"})
        if response and "result" in response:
            result = response["result"]
            print(json.dumps(result, indent=2))
            available_fields = list(result.keys())
            print(f"\nAvailable fields: {', '.join(available_fields)}")
        
        time.sleep(1)
        
        # Test Wifi.GetStatus
        print("\n5. Wifi.GetStatus - WiFi Status")
        print("-" * 60)
        response = send_request(sock, ip, port, "Wifi.GetStatus", {"id": 0})
        if response and "result" in response:
            result = response["result"]
            print(json.dumps(result, indent=2))
            available_fields = list(result.keys())
            print(f"\nAvailable fields: {', '.join(available_fields)}")
        
    finally:
        sock.close()
    
    print("\n" + "=" * 60)
    print("Test complete")


if __name__ == "__main__":
    main()
