"""Test Bat.GetStatus response."""
import socket
import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_bat_status.py <device_ip>")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = 30000
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)
    
    request = {
        "id": 0,
        "method": "Bat.GetStatus",
        "params": {"id": 0}
    }
    
    print(f"Sending Bat.GetStatus to {ip}:{port}")
    sock.sendto(json.dumps(request).encode("utf-8"), (ip, port))
    
    try:
        data, addr = sock.recvfrom(4096)
        response = json.loads(data.decode("utf-8"))
        print("\nBat.GetStatus Response:")
        print(json.dumps(response, indent=2))
        
        if "result" in response:
            result = response["result"]
            print(f"\nAvailable fields: {', '.join(result.keys())}")
    except socket.timeout:
        print("Timeout waiting for response")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
