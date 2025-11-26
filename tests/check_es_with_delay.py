"""Test ES.GetStatus with proper delay after other calls."""
import socket
import json
import sys
import time

def send_request(sock, ip, port, method, params):
    """Send a request and get response."""
    request = {
        "id": 0,
        "method": method,
        "params": params
    }
    
    sock.sendto(json.dumps(request).encode("utf-8"), (ip, port))
    
    try:
        data, addr = sock.recvfrom(4096)
        return json.loads(data.decode("utf-8"))
    except socket.timeout:
        return {"error": "timeout"}

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_es_with_delay.py <device_ip>")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = 30000
    
    print(f"Testing ES.GetStatus sequence to {ip}:{port}")
    print("=" * 60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10.0)
    
    # Test 1: ES.GetStatus immediately
    print("\nTest 1: ES.GetStatus (no previous calls)")
    print("-" * 60)
    response = send_request(sock, ip, port, "ES.GetStatus", {"id": 0})
    print(json.dumps(response, indent=2))
    
    time.sleep(5)
    
    # Test 2: Bat.GetStatus then ES.GetStatus
    print("\nTest 2: Bat.GetStatus followed by ES.GetStatus")
    print("-" * 60)
    print("Calling Bat.GetStatus...")
    response1 = send_request(sock, ip, port, "Bat.GetStatus", {"id": 0})
    if "result" in response1:
        print("✓ Bat.GetStatus successful")
    
    print("Waiting 60 seconds...")
    time.sleep(60)
    
    print("Calling ES.GetStatus...")
    response2 = send_request(sock, ip, port, "ES.GetStatus", {"id": 0})
    print(json.dumps(response2, indent=2))
    
    if "result" in response2:
        result = response2["result"]
        print(f"\n✓ Available fields: {', '.join(result.keys())}")
    
    sock.close()

if __name__ == "__main__":
    main()
