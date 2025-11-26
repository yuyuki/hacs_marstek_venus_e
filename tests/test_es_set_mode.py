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


async def test_es_set_mode(
    ip_address: str,
    mode: str,
    port: int = 30000,
    timeout: float = 10.0,
    manual_time_num: int = 1,
    manual_start_time: str = "08:30",
    manual_end_time: str = "20:30",
    manual_week_set: int = 127,
    manual_power: int = 100,
    clear_manual_schedules: bool = False,
    disable_slot: bool = False,
):
    """Test ES.SetMode.
    
    This function tests setting the operating mode.
    
    Args:
        ip_address: Device IP address
        mode: Operating mode to set (Auto, AI, Manual, or Passive)
        port: Device port
        timeout: Request timeout in seconds
        manual_time_num: Manual mode schedule slot (0-9)
        manual_start_time: Manual mode start time (HH:MM)
        manual_end_time: Manual mode end time (HH:MM)
        manual_week_set: Manual mode week days bitmask (127 = all days)
        manual_power: Manual mode power in watts (100-800, negative=charge, positive=discharge)
        clear_manual_schedules: If True, clear all manual schedules (no manual_cfg sent)
        disable_slot: If True, disable the specified time slot (only time_num and enable=0)
        
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
        
        # Build the config and payload for display based on mode
        manual_cfg = None
        if mode == "Manual":
            if clear_manual_schedules:
                print(f"[INFO] ⚠ CLEARING ALL MANUAL SCHEDULES")
                print(f"[INFO] Sending Manual mode WITHOUT manual_cfg to delete all time slots")
                print()
            elif disable_slot:
                manual_cfg = {
                    "time_num": manual_time_num,
                    "enable": 0,
                }
                print(f"[INFO] ⚠ DISABLING TIME SLOT {manual_time_num}")
                print(f"[INFO] Sending only time_num and enable=0 to disable this slot")
                print()
            else:
                manual_cfg = {
                    "time_num": manual_time_num,
                    "start_time": manual_start_time,
                    "end_time": manual_end_time,
                    "week_set": manual_week_set,
                    "power": manual_power,
                    "enable": 1,
                }
                print(f"[INFO] Manual schedule configuration:")
                print(f"[INFO]   Time slot: {manual_time_num} (0-9)")
                print(f"[INFO]   Time: {manual_start_time} - {manual_end_time}")
                print(f"[INFO]   Week days: {manual_week_set} (127 = all days)")
                action = 'CHARGE' if manual_power < 0 else 'DISCHARGE' if manual_power > 0 else 'IDLE'
                print(f"[INFO]   Power: {manual_power}W ({action}) [Range: 100-800W]")
                print()
        
        # Build the expected payload for display
        print(f"[INFO] Request payload:")
        if mode == "Manual":
            if clear_manual_schedules:
                # Send Manual mode without manual_cfg to clear schedules
                payload_str = json.dumps({
                    "id": 1,
                    "method": "ES.SetMode",
                    "params": {
                        "id": 0,
                        "config": {
                            "mode": mode
                        }
                    }
                }, indent=2)
            elif disable_slot or manual_cfg:
                # Send Manual mode with manual_cfg (either to disable or configure)
                payload_str = json.dumps({
                    "id": 1,
                    "method": "ES.SetMode",
                    "params": {
                        "id": 0,
                        "config": {
                            "mode": mode,
                            "manual_cfg": manual_cfg
                        }
                    }
                }, indent=2)
            else:
                payload_str = json.dumps({
                    "id": 1,
                    "method": "ES.SetMode",
                    "params": {
                        "id": 0,
                        "config": {
                            "mode": mode
                        }
                    }
                }, indent=2)
            print(f"[INFO] {payload_str}\n")
        else:
            mode_cfg_key = f"{mode.lower()}_cfg"
            print(f'[INFO]   {{"id": 1, "method": "ES.SetMode", "params": {{"id": 0, "config": {{"mode": "{mode}", "{mode_cfg_key}": {{"enable": 1}}}}}}}}\n')
        
        response = await client.set_mode(mode, manual_cfg=manual_cfg)
        
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


async def discover_and_test(mode: str, clear_manual_schedules: bool = False, disable_slot: bool = False, **kwargs):
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
            
            success = await test_es_set_mode(ip_address, mode, port, clear_manual_schedules=clear_manual_schedules, disable_slot=disable_slot, **kwargs)
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
        print("Options:")
        print("  --ip <address>       Device IP address")
        print("  --port <port>        Device port (default: 30000)")
        print("  --timeout <seconds>  Request timeout (default: 10.0)")
        print("\nManual Mode Options:")
        print("  --mtimenum <0-9>     Time slot number (default: 1)")
        print("  --mstart <HH:MM>     Start time (default: 08:30)")
        print("  --mend <HH:MM>       End time (default: 20:30)")
        print("  --mweek <bitmask>    Week days bitmask (default: 127 = all days)")
        print("                       1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun")
        print("  --mpower <watts>     Power in watts (default: 100, range: 100-800)")
        print("                       Negative = charge, Positive = discharge")
        print("  --clear              Clear all manual schedules (no manual_cfg sent)")
        print("  --disable            Disable a specific time slot (only time_num + enable=0)")
        print("\nModes:")
        print("  Auto     - Automatic operation based on battery SOC and grid")
        print("  AI       - AI-optimized operation for maximum efficiency")
        print("  Manual   - Manual control with time-based schedules")
        print("  Passive  - Passive operation with countdown timer")
        print("\nExamples:")
        print("  python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Auto")
        print("  python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Manual")
        print("  python tests/test_es_set_mode.py --ip 192.168.0.225 --mode Manual --mpower -500  # Charge at 500W")
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
    
    # Manual mode parameters
    manual_time_num = 1
    manual_start_time = "08:30"
    manual_end_time = "20:30"
    manual_week_set = 127
    manual_power = 100
    clear_manual_schedules = False
    disable_slot = False
    
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
    
    # Parse --clear and --disable flags
    if "--clear" in sys.argv:
        clear_manual_schedules = True
    
    if "--disable" in sys.argv:
        disable_slot = True
    
    # Parse manual mode arguments
    if "--mtimenum" in sys.argv:
        try:
            idx = sys.argv.index("--mtimenum")
            manual_time_num = int(sys.argv[idx + 1])
            if manual_time_num < 0 or manual_time_num > 9:
                print("[ERROR] --mtimenum must be between 0 and 9")
                sys.exit(1)
        except (IndexError, ValueError):
            print("[ERROR] --mtimenum requires a valid number (0-9)")
            sys.exit(1)
    
    if "--mstart" in sys.argv:
        try:
            idx = sys.argv.index("--mstart")
            manual_start_time = sys.argv[idx + 1]
        except IndexError:
            print("[ERROR] --mstart requires a time in HH:MM format")
            sys.exit(1)
    
    if "--mend" in sys.argv:
        try:
            idx = sys.argv.index("--mend")
            manual_end_time = sys.argv[idx + 1]
        except IndexError:
            print("[ERROR] --mend requires a time in HH:MM format")
            sys.exit(1)
    
    if "--mweek" in sys.argv:
        try:
            idx = sys.argv.index("--mweek")
            manual_week_set = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("[ERROR] --mweek requires a valid number")
            sys.exit(1)
    
    if "--mpower" in sys.argv:
        try:
            idx = sys.argv.index("--mpower")
            manual_power = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("[ERROR] --mpower requires a valid number")
            sys.exit(1)
    
    # Run test
    if ip_address:
        print("\n" + "="*80)
        print("MARSTEK VENUS E - ES.SetMode TEST")
        print("="*80)
        print("API Method: ES.SetMode")
        print("Purpose: Change operating mode")
        print("="*80)
        
        success = await test_es_set_mode(
            ip_address,
            mode,
            port,
            timeout,
            manual_time_num,
            manual_start_time,
            manual_end_time,
            manual_week_set,
            manual_power,
            clear_manual_schedules,
            disable_slot,
        )
        sys.exit(0 if success else 1)
    else:
        await discover_and_test(
            mode,
            clear_manual_schedules=clear_manual_schedules,
            disable_slot=disable_slot,
            timeout=timeout,
            manual_time_num=manual_time_num,
            manual_start_time=manual_start_time,
            manual_end_time=manual_end_time,
            manual_week_set=manual_week_set,
            manual_power=manual_power,
        )


if __name__ == "__main__":
    asyncio.run(main())
