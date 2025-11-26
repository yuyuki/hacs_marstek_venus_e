"""Test script to clear all manual schedules by disabling each slot.

This test loops through all 10 time slots (0-9) and disables each one individually.
"""
import asyncio
import sys
import importlib.util
from pathlib import Path

# Load udp_client module directly without importing the whole integration
udp_client_path = Path(__file__).parent.parent / "custom_components" / "hacs_marstek_venus_e" / "udp_client.py"
spec = importlib.util.spec_from_file_location("udp_client", udp_client_path)
udp_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(udp_client_module)

MarstekUDPClient = udp_client_module.MarstekUDPClient


async def disable_all_slots(ip_address: str, port: int = 30000, timeout: float = 10.0):
    """Disable all manual schedule slots (0-9).
    
    Args:
        ip_address: Device IP address
        port: Device port
        timeout: Request timeout in seconds
    """
    print("\n" + "="*80)
    print("DISABLE ALL MANUAL SCHEDULE SLOTS (0-9)")
    print("="*80)
    print(f"Target Device: {ip_address}:{port}")
    print("-"*80)
    
    client = MarstekUDPClient(ip_address, port, timeout=timeout)
    
    # Try to disable each slot from 0 to 9
    success_count = 0
    failed_slots = []
    
    for slot_num in range(10):
        print(f"\n[INFO] Attempting to disable slot {slot_num}...")
        
        # Try with full schedule configuration but enable=0
        manual_cfg = {
            "time_num": slot_num,
            "start_time": "00:00",
            "end_time": "23:59",
            "week_set": 127,
            "power": 100,
            "enable": 0,
        }
        
        try:
            response = await client.set_mode("Manual", manual_cfg=manual_cfg)
            
            if response.get("set_result"):
                print(f"[OK] ✓ Slot {slot_num} disabled successfully")
                success_count += 1
            else:
                print(f"[WARN] Slot {slot_num} - unexpected response: {response}")
                failed_slots.append(slot_num)
                
        except Exception as e:
            print(f"[FAIL] ✗ Slot {slot_num} - Error: {e}")
            failed_slots.append(slot_num)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Successfully disabled: {success_count}/10 slots")
    
    if failed_slots:
        print(f"Failed slots: {', '.join(map(str, failed_slots))}")
    else:
        print("All slots disabled!")
    
    print("\n⚠ Please verify in the official Marstek app that all schedules are cleared.")
    print("="*80)
    print()
    
    return success_count == 10


async def main():
    """Main entry point."""
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) < 2:
        print("\nClear All Manual Schedules Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_clear_all_schedules.py --ip <ip_address> [options]")
        print("\nOptions:")
        print("  --ip <address>       Device IP address (required)")
        print("  --port <port>        Device port (default: 30000)")
        print("  --timeout <seconds>  Request timeout (default: 10.0)")
        print("\nExample:")
        print("  python tests/test_clear_all_schedules.py --ip 192.168.0.225")
        print("="*80)
        print()
        return
    
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
    else:
        print("[ERROR] --ip argument is required")
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
    success = await disable_all_slots(ip_address, port, timeout)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
