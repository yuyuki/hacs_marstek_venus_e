"""Direct UDP test to verify Marstek protocol works."""
import socket
import json
import time
import sys

def test_direct_udp(ip_address, port=30000, timeout=15):
    """Send discovery probe directly to a device IP and wait for response."""
    print(f"\nDirect UDP Test to {ip_address}:{port}")
    print("="*60)
    
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    # Build probe payload
    probe = {
        "id": 0,
        "method": "Marstek.GetDevice",
        "params": {
            "ble_mac": "0"
        }
    }
    
    probe_json = json.dumps(probe)
    print(f"Sending probe: {probe_json}")
    print(f"Probe size: {len(probe_json.encode())} bytes\n")
    
    try:
        # Send to device
        sock.sendto(probe_json.encode("utf-8"), (ip_address, port))
        print(f"✓ Probe sent to {ip_address}:{port}")
        
        # Wait for response
        print(f"Waiting up to {timeout} seconds for response...")
        data, addr = sock.recvfrom(4096)
        
        print(f"\n✓ Received {len(data)} bytes from {addr}")
        print(f"Raw response: {data[:200]}")  # First 200 bytes
        
        try:
            response = json.loads(data.decode("utf-8"))
            print(f"\n✓ Valid JSON response:")
            print(json.dumps(response, indent=2))
            return True
        except json.JSONDecodeError as e:
            print(f"\n✗ Response is not valid JSON: {e}")
            return False
            
    except socket.timeout:
        print(f"✗ Timeout - no response from device after {timeout} seconds")
        return False
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        return False
    finally:
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Direct UDP Discovery Test")
        print("="*60)
        print("\nUsage: python test_direct_udp.py <device_ip> [port] [timeout]")
        print("\nExample:")
        print("  python test_direct_udp.py 192.168.0.225")
        print("  python test_direct_udp.py 192.168.0.225 30000 5")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    
    success = test_direct_udp(ip, port, timeout)
    sys.exit(0 if success else 1)
