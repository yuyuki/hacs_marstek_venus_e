"""Test script for Marstek.GetDevice API function (Device Discovery).

This test verifies that the Marstek Venus E device can be discovered
on the local network using UDP broadcast.
"""
import asyncio
import json
import sys
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


async def test_marstek_get_device(timeout: float = 15.0):
    """Test Marstek.GetDevice (Discovery).
    
    This function tests device discovery using UDP broadcast.
    
    Args:
        timeout: Discovery timeout in seconds
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST: Marstek.GetDevice (Device Discovery)")
    print("="*80)
    print("Method: Marstek.GetDevice")
    print("Description: Discover Marstek Venus E devices on local network via UDP broadcast")
    print(f"Timeout: {timeout} seconds")
    print("Port: 30000")
    print("-"*80)
    
    try:
        print("\n[INFO] Sending broadcast discovery probe to 255.255.255.255:30000...")
        print("[INFO] Waiting for device responses...\n")
        
        devices = await MarstekUDPClient.discover(timeout=timeout, port=30000)
        
        if devices:
            print(f"[OK] Discovery completed successfully!")
            print(f"[OK] Found {len(devices)} device(s)\n")
            
            for idx, (ip, port, payload) in enumerate(devices, 1):
                print(f"Device #{idx}:")
                print(f"  IP Address: {ip}")
                print(f"  Port: {port}")
                
                result = payload.get("result", {})
                if result:
                    print(f"  Device Type: {result.get('device', 'Unknown')}")
                    print(f"  BLE MAC: {result.get('ble_mac', 'N/A')}")
                    print(f"  WiFi MAC: {result.get('wifi_mac', 'N/A')}")
                    print(f"  WiFi SSID: {result.get('wifi_name', 'N/A')}")
                    print(f"  Firmware Version: {result.get('ver', 'N/A')}")
                    print(f"  Source: {payload.get('src', 'N/A')}")
                
                print(f"\n  Full Response:")
                print("  " + "-"*76)
                print("  " + json.dumps(payload, indent=2).replace("\n", "\n  "))
                print()
            
            print("="*80)
            print("TEST RESULT: ✓ PASSED")
            print("="*80)
            print(f"\nSummary: Successfully discovered {len(devices)} Marstek Venus E device(s)")
            print()
            
            return True
        else:
            print("[WARN] No devices found on the network")
            print("\nPossible reasons:")
            print("  • No Marstek Venus E devices powered on")
            print("  • Devices on different network/subnet")
            print("  • Firewall blocking UDP broadcast on port 30000")
            print("  • Device not connected to WiFi")
            
            print("\n" + "="*80)
            print("TEST RESULT: ✗ FAILED - No devices found")
            print("="*80)
            print()
            
            return False
            
    except Exception as err:
        print(f"[FAIL] Discovery error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*80)
        print("TEST RESULT: ✗ FAILED - Exception occurred")
        print("="*80)
        print()
        
        return False


async def main():
    """Main entry point."""
    print("\n")
    print("="*80)
    print("MARSTEK VENUS E - Marstek.GetDevice TEST")
    print("="*80)
    print("API Method: Marstek.GetDevice")
    print("Purpose: Device discovery via UDP broadcast")
    print("="*80)
    
    # Parse timeout from command line
    timeout = 15.0
    if "--timeout" in sys.argv:
        try:
            timeout_index = sys.argv.index("--timeout")
            timeout = float(sys.argv[timeout_index + 1])
        except (IndexError, ValueError):
            print("[WARN] Invalid timeout value, using default 15.0 seconds")
    
    # Run test
    success = await test_marstek_get_device(timeout)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nMarstek.GetDevice Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_marstek_get_device.py [--timeout <seconds>]")
        print("\nOptions:")
        print("  --timeout <seconds>  Discovery timeout (default: 15.0)")
        print("\nExamples:")
        print("  python tests/test_marstek_get_device.py")
        print("  python tests/test_marstek_get_device.py --timeout 20")
        print("="*80)
        print()
    else:
        asyncio.run(main())
