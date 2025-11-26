"""Test ES.GetStatus response with retry."""
import socket
import json
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_es_status.py <device_ip>")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = 30000
    
    request = {
        "id": 0,
        "method": "ES.GetStatus",
        "params": {"id": 0}
    }
    
    print(f"Testing ES.GetStatus to {ip}:{port}")
    
    # Try multiple times with increasing timeout
    for attempt in range(1, 4):
        print(f"\nAttempt {attempt}/3...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10.0)  # 10 second timeout
        
        try:
            print(f"Sending ES.GetStatus request...")
            sock.sendto(json.dumps(request).encode("utf-8"), (ip, port))
            
            print(f"Waiting for response (timeout: 10s)...")
            data, addr = sock.recvfrom(4096)
            response = json.loads(data.decode("utf-8"))
            
            print("\n✓ ES.GetStatus Response:")
            print(json.dumps(response, indent=2))
            
            if "result" in response:
                result = response["result"]
                print(f"\nAvailable fields: {', '.join(result.keys())}")
            
            sock.close()
            return  # Success!
            
        except socket.timeout:
            print(f"✗ Timeout on attempt {attempt}")
            sock.close()
            if attempt < 3:
                print("Waiting 2 seconds before retry...")
                time.sleep(2)
        except Exception as e:
            print(f"✗ Error: {e}")
            sock.close()
            if attempt < 3:
                time.sleep(2)
    
    print("\n✗ Failed after 3 attempts")

if __name__ == "__main__":
    main()
