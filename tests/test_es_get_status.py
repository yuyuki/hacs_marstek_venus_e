"""Test script for ES.GetStatus API function.

This test verifies that the energy system status can be retrieved
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


async def test_es_get_status(ip_address: str, port: int = 30000, timeout: float = 5.0):
    """Test ES.GetStatus.
    
    This function tests getting energy system status.
    
    Args:
        ip_address: Device IP address
        port: Device port
        timeout: Request timeout in seconds
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST: ES.GetStatus (Energy System Status)")
    print("="*80)
    print("Method: ES.GetStatus")
    print("Description: Get current energy system status (battery, PV, grid, power flow)")
    print(f"Target Device: {ip_address}:{port}")
    print(f"Timeout: {timeout} seconds")
    print("-"*80)
    
    try:
        client = MarstekUDPClient(ip_address, port, timeout=timeout)
        
        print("\n[INFO] Sending ES.GetStatus request...")
        print("[INFO] Request payload: {\"id\": 1, \"method\": \"ES.GetStatus\", \"params\": {\"id\": 0}}\n")
        
        # Attempt to get energy system status
        status = await client.get_energy_system_status()
        
        print("[OK] Response received successfully!\n")
        print("Energy System Status:")
        print("-"*80)
        print(json.dumps(status, indent=2))
        
        # Display key information in a formatted table
        print("\n" + "-"*80)
        print("Key Metrics:")
        print("-"*80)
        print(f"{'Metric':<30} {'Value':<20} {'Unit':<10}")
        print("-"*80)
        print(f"{'Battery SOC':<30} {status.get('bat_soc', 'N/A'):<20} {'%':<10}")
        print(f"{'Battery Capacity':<30} {status.get('bat_cap', 'N/A'):<20} {'Wh':<10}")
        print(f"{'Battery Power':<30} {status.get('bat_power', 'N/A'):<20} {'W':<10}")
        print(f"{'PV Power':<30} {status.get('pv_power', 'N/A'):<20} {'W':<10}")
        print(f"{'On-Grid Power':<30} {status.get('ongrid_power', 'N/A'):<20} {'W':<10}")
        print(f"{'Off-Grid Power':<30} {status.get('offgrid_power', 'N/A'):<20} {'W':<10}")
        print(f"{'Total PV Energy':<30} {status.get('total_pv_energy', 'N/A'):<20} {'kWh':<10}")
        print(f"{'Total Grid Output':<30} {status.get('total_grid_output_energy', 'N/A'):<20} {'kWh':<10}")
        print(f"{'Total Grid Input':<30} {status.get('total_grid_input_energy', 'N/A'):<20} {'kWh':<10}")
        print(f"{'Total Load Energy':<30} {status.get('total_load_energy', 'N/A'):<20} {'kWh':<10}")
        print("-"*80)
        
        print("\n" + "="*80)
        print("TEST RESULT: ✓ PASSED")
        print("="*80)
        print("\nSummary: Successfully retrieved energy system status")
        print()
        
        return True
        
    except asyncio.TimeoutError:
        print(f"[FAIL] Request timed out after {timeout} seconds")
        print("\n[INFO] Note: Some Marstek devices may only respond to broadcast requests,")
        print("[INFO] not to unicast requests. This is a known limitation.")
        print("[INFO] If this test fails, try running test_marstek_get_device.py first")
        print("[INFO] to verify the device is discoverable.")
        
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
    """Discover device first, then test ES.GetStatus."""
    print("\n" + "="*80)
    print("MARSTEK VENUS E - ES.GetStatus TEST")
    print("="*80)
    print("API Method: ES.GetStatus")
    print("Purpose: Retrieve energy system status")
    print("="*80)
    
    print("\n[INFO] No IP address provided, attempting discovery first...")
    
    try:
        devices = await MarstekUDPClient.discover(timeout=10.0, port=30000)
        
        if devices:
            ip_address, port, _ = devices[0]
            print(f"[OK] Found device at {ip_address}:{port}")
            print(f"[INFO] Testing ES.GetStatus on discovered device...\n")
            
            success = await test_es_get_status(ip_address, port)
            sys.exit(0 if success else 1)
        else:
            print("[FAIL] No devices found during discovery")
            print("\nPlease provide the device IP address manually:")
            print("  python tests/test_es_get_status.py --ip <ip_address>")
            sys.exit(1)
            
    except Exception as err:
        print(f"[FAIL] Discovery failed: {err}")
        sys.exit(1)


async def main():
    """Main entry point."""
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nES.GetStatus Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_es_get_status.py --ip <ip_address> [options]")
        print("  python tests/test_es_get_status.py  (auto-discover)")
        print("\nOptions:")
        print("  --ip <address>       Device IP address")
        print("  --port <port>        Device port (default: 30000)")
        print("  --timeout <seconds>  Request timeout (default: 5.0)")
        print("\nExamples:")
        print("  python tests/test_es_get_status.py --ip 192.168.0.225")
        print("  python tests/test_es_get_status.py --ip 192.168.0.225 --timeout 10")
        print("  python tests/test_es_get_status.py")
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
        print("MARSTEK VENUS E - ES.GetStatus TEST")
        print("="*80)
        print("API Method: ES.GetStatus")
        print("Purpose: Retrieve energy system status")
        print("="*80)
        
        success = await test_es_get_status(ip_address, port, timeout)
        sys.exit(0 if success else 1)
    else:
        await discover_and_test()


if __name__ == "__main__":
    asyncio.run(main())
