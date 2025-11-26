"""Test script for ES.SetMode API function.

This test allows you to change the operating mode of the Marstek Venus E device.
It's designed to run one mode change at a time so you can verify in the official app.
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


async def test_es_set_mode(ip_address: str, mode: str, port: int = 30000, timeout: float = 10.0):
    """Test ES.SetMode.
    
    This function tests setting the operating mode.
    
    Args:
        ip_address: Device IP address
        mode: Operating mode to set (Auto, AI, Manual, or Passive)
        port: Device port
        timeout: Request timeout in seconds
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST: ES.SetMode (Set Operating Mode)")
    print("="*80)
    print("Method: ES.SetMode")
    print("Description: Change the device operating mode")
    print(f"Target Device: {ip_address}:{port}")
    print(f"Target Mode: {mode}")
    print(f"Timeout: {timeout} seconds")
    print("-"*80)
    
    # Validate mode
    valid_modes = ["Auto", "AI", "Manual", "Passive"]
    if mode not in valid_modes:
        print(f"[ERROR] Invalid mode '{mode}'")
        print(f"[ERROR] Valid modes are: {', '.join(valid_modes)}")
        return False
    
    # Display mode description
    mode_descriptions = {
        "Auto": "Automatic operation based on battery SOC and grid conditions",
        "AI": "AI-optimized operation for maximum efficiency",
        "Manual": "Manual control with time-based charging/discharging schedules",
        "Passive": "Passive operation with countdown timer"
    }
    
    print(f"\n[INFO] Mode Description:")
    print(f"[INFO] {mode_descriptions.get(mode, 'Unknown mode')}")
    print()
    
    try:
        client = MarstekUDPClient(ip_address, port, timeout=timeout)
        
        # Get current mode first
        print("[INFO] Getting current mode before change...")
        try:
            current_mode_data = await client.get_energy_system_mode()
            current_mode = current_mode_data.get('mode', 'Unknown')
            print(f"[INFO] Current mode: {current_mode}\n")
            
            if current_mode == mode:
                print(f"[INFO] Device is already in {mode} mode!")
                print(f"[INFO] No change needed, but will send command anyway to verify.\n")
        except Exception as e:
            print(f"[WARN] Could not get current mode: {e}")
            print(f"[WARN] Proceeding with mode change anyway...\n")
        
        # Set new mode
        print(f"[INFO] Sending ES.SetMode request to change mode to: {mode}")
        
        # Build the expected payload for display
        mode_cfg_key = f"{mode.lower()}_cfg"
        print(f"[INFO] Request payload:")
        print(f'[INFO]   {{"id": 1, "method": "ES.SetMode", "params": {{"id": 0, "config": {{"mode": "{mode}", "{mode_cfg_key}": {{"enable": 1}}}}}}}}\n')
        
        response = await client.set_mode(mode)
        
        print("[OK] Response received successfully!\n")
        print("Response Data:")
        print("-"*80)
        print(json.dumps(response, indent=2))
        print("-"*80)
        
        # Verify the change
        print(f"\n[INFO] Waiting 2 seconds before verifying mode change...")
        await asyncio.sleep(2)
        
        print(f"[INFO] Verifying mode change by reading current mode...")
        try:
            verify_mode_data = await client.get_energy_system_mode()
            new_mode = verify_mode_data.get('mode', 'Unknown')
            
            print(f"\n[INFO] Verification Result:")
            print(f"[INFO] Requested mode: {mode}")
            print(f"[INFO] Current mode: {new_mode}")
            
            if new_mode == mode:
                print(f"[OK] ✓ Mode successfully changed to {mode}!")
            else:
                print(f"[WARN] ⚠ Mode is {new_mode}, expected {mode}")
                print(f"[WARN] The device may need more time to process the change")
                print(f"[WARN] Please verify in the official app")
        except Exception as e:
            print(f"[WARN] Could not verify mode change: {e}")
            print(f"[INFO] Please verify in the official app")
        
        print("\n" + "="*80)
        print("TEST RESULT: ✓ PASSED")
        print("="*80)
        print(f"\nSummary: Successfully sent command to change mode to: {mode}")
        print(f"\n⚠ IMPORTANT: Please verify the mode change in the official Marstek app!")
        print(f"⚠ Check that the device is now in {mode} mode.")
        print()
        
        return True
        
    except asyncio.TimeoutError:
        print(f"[FAIL] Request timed out after {timeout} seconds")
        print("\n[INFO] Possible reasons:")
        print("[INFO]   - Device IP address is incorrect")
        print("[INFO]   - Device is powered off or disconnected from WiFi")
        print("[INFO]   - Firewall is blocking port 30000")
        print("[INFO]   - Network connectivity issues")
        
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


async def discover_and_test(mode: str):
    """Discover device first, then test ES.SetMode."""
    print("\n" + "="*80)
    print("MARSTEK VENUS E - ES.SetMode TEST")
    print("="*80)
    print("API Method: ES.SetMode")
    print("Purpose: Change operating mode")
    print("="*80)
    
    print("\n[INFO] No IP address provided, attempting discovery first...")
    
    try:
        devices = await MarstekUDPClient.discover(timeout=10.0, port=30000)
        
        if devices:
            ip_address, port, _ = devices[0]
            print(f"[OK] Found device at {ip_address}:{port}")
            print(f"[INFO] Testing ES.SetMode on discovered device...\n")
            
            success = await test_es_set_mode(ip_address, mode, port)
            sys.exit(0 if success else 1)
        else:
            print("[FAIL] No devices found during discovery")
            print("\nPlease provide the device IP address manually:")
            print("  python tests/test_es_set_mode.py --ip <ip_address> --mode <mode>")
            sys.exit(1)
            
    except Exception as err:
        print(f"[FAIL] Discovery failed: {err}")
        sys.exit(1)


async def main():
    """Main entry point."""
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nES.SetMode Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_es_set_mode.py --ip <ip_address> --mode <mode> [options]")
        print("  python tests/test_es_set_mode.py --mode <mode>  (auto-discover)")
        print("\nRequired:")
        print("  --mode <mode>        Operating mode: Auto, AI, Manual, or Passive")
        print("\nOptions:")
        print("  --ip <address>       Device IP address")
        print("  --port <port>        Device port (default: 30000)")
        print("  --timeout <seconds>  Request timeout (default: 10.0)")
        print("\nModes:")
        print("  Auto     - Automatic operation based on battery SOC and grid")
        print("  AI       - AI-optimized operation for maximum efficiency")
        print("  Manual   - Manual control with time-based schedules")
        print("  Passive  - Passive operation with countdown timer")
        print("\nExamples:")
        print("  python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Auto")
        print("  python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Manual")
        print("  python tests/test_es_set_mode.py --mode AI  (auto-discover)")
        print("\nTesting Workflow:")
        print("  1. Run this test with one mode")
        print("  2. Check the official Marstek app to verify the change")
        print("  3. Run again with a different mode")
        print("  4. Verify again in the app")
        print("="*80)
        print()
        return
    
    # Parse --mode argument (required)
    if "--mode" not in sys.argv:
        print("[ERROR] --mode argument is required")
        print("\nUsage: python tests/test_es_set_mode.py --mode <mode> [--ip <ip_address>]")
        print("\nValid modes: Auto, AI, Manual, Passive")
        print("\nFor more help: python tests/test_es_set_mode.py --help")
        sys.exit(1)
    
    try:
        mode_index = sys.argv.index("--mode")
        mode = sys.argv[mode_index + 1]
    except (IndexError, ValueError):
        print("[ERROR] --mode requires a mode argument")
        print("Valid modes: Auto, AI, Manual, Passive")
        sys.exit(1)
    
    # Validate mode
    valid_modes = ["Auto", "AI", "Manual", "Passive"]
    if mode not in valid_modes:
        print(f"[ERROR] Invalid mode '{mode}'")
        print(f"Valid modes: {', '.join(valid_modes)}")
        sys.exit(1)
    
    ip_address = None
    port = 30000
    timeout = 10.0
    
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
        print("MARSTEK VENUS E - ES.SetMode TEST")
        print("="*80)
        print("API Method: ES.SetMode")
        print("Purpose: Change operating mode")
        print("="*80)
        
        success = await test_es_set_mode(ip_address, mode, port, timeout)
        sys.exit(0 if success else 1)
    else:
        await discover_and_test(mode)


if __name__ == "__main__":
    asyncio.run(main())
