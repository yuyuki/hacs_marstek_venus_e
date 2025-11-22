"""Test script for Marstek Venus E device discovery."""
import asyncio
import json
import logging
import importlib.util
from pathlib import Path

# Setup logging to see debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load udp_client module directly without importing the whole integration
udp_client_path = Path(__file__).parent.parent / "custom_components" / "hacs_marstek_venus_e" / "udp_client.py"
spec = importlib.util.spec_from_file_location("udp_client", udp_client_path)
udp_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(udp_client_module)

MarstekUDPClient = udp_client_module.MarstekUDPClient


async def main():
    """Test device discovery."""
    print("\n" + "="*60)
    print("TEST: Device Discovery")
    print("="*60)
    print("Sending discovery probe to broadcast address 255.255.255.255:30000...")
    print("Waiting up to 15 seconds for responses...\n")
    
    try:
        devices = await MarstekUDPClient.discover(timeout=15.0, port=30000)
        
        if devices:
            print(f"[OK] Discovery completed successfully")
            print(f"[OK] Found {len(devices)} device(s)\n")
            
            print("Devices Found:")
            print("-" * 60)
            for idx, (ip, port, payload) in enumerate(devices, 1):
                print(f"\nDevice #{idx}:")
                print(f"  IP Address: {ip}")
                print(f"  Port: {port}")
                print(f"  Full Response: {json.dumps(payload, indent=4)}")
                
                # Extract device info if available
                result = payload.get("result", {})
                if result:
                    print(f"\n  Device Type: {result.get('device', 'Unknown')}")
                    print(f"  MAC Address: {result.get('ble_mac', 'N/A')}")
                    print(f"  WiFi MAC: {result.get('wifi_mac', 'N/A')}")
                    print(f"  WiFi SSID: {result.get('wifi_name', 'N/A')}")
                    print(f"  Firmware Ver: {result.get('ver', 'N/A')}")
            
            print("\n" + "="*60)
            print("TEST PASSED")
            print("="*60)
        else:
            print("[WARN] No devices found on the network.")
            print("  This is normal if:")
            print("  - No Marstek Venus E devices are on the network")
            print("  - The device is not powered on")
            print("  - The device is on a different network/subnet")
            print("  - Network/firewall blocks UDP broadcast on port 30000")
            
            print("\n" + "="*60)
            print("TEST PASSED (no devices found)")
            print("="*60)
            
    except Exception as err:
        print(f"[FAIL] Discovery failed with error:")
        print(f"  {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*60)
        print("TEST FAILED")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
