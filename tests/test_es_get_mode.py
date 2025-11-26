"""Test script for ES.GetMode API function.

This test verifies that the operating mode can be retrieved
from a Marstek Venus E device.
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


async def test_es_get_mode(ip_address: str, port: int = 30000, timeout: float = 5.0):
    """Test ES.GetMode.
    
    This function tests getting the current operating mode.
    
    Args:
        ip_address: Device IP address
        port: Device port
        timeout: Request timeout in seconds
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST: ES.GetMode (Operating Mode)")
    print("="*80)
    print("Method: ES.GetMode")
    print("Description: Get current operating mode (Auto, AI, Manual, Passive)")
    print(f"Target Device: {ip_address}:{port}")
    print(f"Timeout: {timeout} seconds")
    print("-"*80)
    
    try:
        client = MarstekUDPClient(ip_address, port, timeout=timeout)
        
        print("\n[INFO] Sending ES.GetMode request...")
        print("[INFO] Request payload: {\"id\": 1, \"method\": \"ES.GetMode\", \"params\": {\"id\": 0}}\n")
        
        # Attempt to get operating mode
        mode_data = await client.get_energy_system_mode()
        
        print("[OK] Response received successfully!\n")
        print("Operating Mode Data:")
        print("-"*80)
        print(json.dumps(mode_data, indent=2))
        
        # Display key information
        print("\n" + "-"*80)
        print("Current Configuration:")
        print("-"*80)
        
        mode = mode_data.get('mode', 'Unknown')
        print(f"\nOperating Mode: {mode}")
        
        # Display additional status information
        if 'bat_soc' in mode_data:
            print(f"Battery SOC: {mode_data.get('bat_soc')}%")
        if 'ongrid_power' in mode_data:
            print(f"On-Grid Power: {mode_data.get('ongrid_power')} W")
        if 'offgrid_power' in mode_data:
            print(f"Off-Grid Power: {mode_data.get('offgrid_power')} W")
        
        # Display CT meter information if available
        ct_state = mode_data.get('ct_state', 0)
        if ct_state:
            print(f"\nCT Meter Status: Connected")
            print(f"  Phase A Power: {mode_data.get('a_power', 0)} W")
            print(f"  Phase B Power: {mode_data.get('b_power', 0)} W")
            print(f"  Phase C Power: {mode_data.get('c_power', 0)} W")
            print(f"  Total Power: {mode_data.get('total_power', 0)} W")
        else:
            print(f"\nCT Meter Status: Not connected")
        
        # Display mode-specific configuration
        if mode == "Manual":
            print("\n[INFO] Device is in Manual mode")
            manual_cfg = mode_data.get('manual_cfg', {})
            if manual_cfg:
                print("Manual Mode Configuration:")
                for key, value in manual_cfg.items():
                    print(f"  {key}: {value}")
        elif mode == "Passive":
            print("\n[INFO] Device is in Passive mode")
            print(f"  Passive Power: {mode_data.get('passive_power', 'N/A')} W")
            print(f"  Countdown Time: {mode_data.get('cd_time', 'N/A')} seconds")
        elif mode == "AI":
            print("\n[INFO] Device is in AI mode (AI-optimized operation)")
        elif mode == "Auto":
            print("\n[INFO] Device is in Auto mode (automatic operation)")
        
        print("-"*80)
        
        print("\n" + "="*80)
        print("TEST RESULT: ✓ PASSED")
        print("="*80)
        print(f"\nSummary: Successfully retrieved operating mode: {mode}")
        print()
        
        return True
        
    except asyncio.TimeoutError:
        print(f"[FAIL] Request timed out after {timeout} seconds")
        print("\n[INFO] Note: Some Marstek devices may only respond to broadcast requests,")
        print("[INFO] not to unicast requests. However, ES.GetMode usually works with unicast.")
        print("[INFO] If this test fails, verify:")
        print("[INFO]   - Device IP address is correct")
        print("[INFO]   - Device is powered on and connected to WiFi")
        print("[INFO]   - No firewall is blocking port 30000")
        
        print("\n" + "="*80)
        print("TEST RESULT: ✗ FAILED - Timeout")
        print("="*80)
        print()
        
        return False
        
    except Exception as err:
        print(f"[FAIL] Error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*80)
        print("TEST RESULT: ✗ FAILED - Exception")
        print("="*80)
        print()
        
        return False


async def discover_and_test():
    """Discover device first, then test ES.GetMode."""
    print("\n" + "="*80)
    print("MARSTEK VENUS E - ES.GetMode TEST")
    print("="*80)
    print("API Method: ES.GetMode")
    print("Purpose: Retrieve current operating mode")
    print("="*80)
    
    print("\n[INFO] No IP address provided, attempting discovery first...")
    
    try:
        devices = await MarstekUDPClient.discover(timeout=10.0, port=30000)
        
        if devices:
            ip_address, port, _ = devices[0]
            print(f"[OK] Found device at {ip_address}:{port}")
            print(f"[INFO] Testing ES.GetMode on discovered device...\n")
            
            success = await test_es_get_mode(ip_address, port)
            sys.exit(0 if success else 1)
        else:
            print("[FAIL] No devices found during discovery")
            print("\nPlease provide the device IP address manually:")
            print("  python tests/test_es_get_mode.py --ip <ip_address>")
            sys.exit(1)
            
    except Exception as err:
        print(f"[FAIL] Discovery failed: {err}")
        sys.exit(1)


async def main():
    """Main entry point."""
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nES.GetMode Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_es_get_mode.py --ip <ip_address> [options]")
        print("  python tests/test_es_get_mode.py  (auto-discover)")
        print("\nOptions:")
        print("  --ip <address>       Device IP address")
        print("  --port <port>        Device port (default: 30000)")
        print("  --timeout <seconds>  Request timeout (default: 5.0)")
        print("\nExamples:")
        print("  python tests/test_es_get_mode.py --ip 192.168.0.225")
        print("  python tests/test_es_get_mode.py --ip 192.168.0.225 --timeout 10")
        print("  python tests/test_es_get_mode.py")
        print("="*80)
        print()
        return
    
    ip_address = None
    port = 30000
    timeout = 5.0
    
    # Parse --ip argument
    if "--ip" in sys.argv:
        try:
            ip_index = sys.argv.index("--ip")
            ip_address = sys.argv[ip_index + 1]
        except (IndexError, ValueError):
            print("[ERROR] --ip requires an IP address argument")
            sys.exit(1)
    
    # Parse --port argument
    if "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            port = int(sys.argv[port_index + 1])
        except (IndexError, ValueError):
            print("[ERROR] --port requires a valid port number")
            sys.exit(1)
    
    # Parse --timeout argument
    if "--timeout" in sys.argv:
        try:
            timeout_index = sys.argv.index("--timeout")
            timeout = float(sys.argv[timeout_index + 1])
        except (IndexError, ValueError):
            print("[ERROR] --timeout requires a valid number")
            sys.exit(1)
    
    # Run test
    if ip_address:
        print("\n" + "="*80)
        print("MARSTEK VENUS E - ES.GetMode TEST")
        print("="*80)
        print("API Method: ES.GetMode")
        print("Purpose: Retrieve current operating mode")
        print("="*80)
        
        success = await test_es_get_mode(ip_address, port, timeout)
        sys.exit(0 if success else 1)
    else:
        await discover_and_test()


if __name__ == "__main__":
    asyncio.run(main())
