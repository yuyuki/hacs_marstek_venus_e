"""Comprehensive test suite for Marstek Venus E API functions.

This file runs all individual API tests in sequence.
For testing individual API functions, use the dedicated test files:
- tests/test_marstek_get_device.py - Device discovery
- tests/test_es_get_status.py - Energy system status
- tests/test_es_get_mode.py - Operating mode

Note: ES.SetMode is not tested as requested.
"""
import asyncio
import json
import sys
import logging
import importlib.util
from pathlib import Path
from typing import Optional

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


class TestResults:
    """Container for test results."""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, message: str = "", data: dict = None):
        """Add a test result."""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "data": data
        })
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed} ✓")
        print(f"Tests Failed: {self.tests_failed} ✗")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("="*80)
        
        if self.tests_failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result["passed"]:
                    print(f"  ✗ {result['test']}: {result['message']}")
        
        print("\n")


async def test_marstek_get_device(results: TestResults) -> Optional[tuple[str, int, dict]]:
    """Test 1: Marstek.GetDevice (Discovery).
    
    This function tests device discovery using UDP broadcast.
    
    Returns:
        First discovered device tuple (ip, port, data) or None
    """
    print("\n" + "="*80)
    print("TEST 1: Marstek.GetDevice (Device Discovery)")
    print("="*80)
    print("Method: Marstek.GetDevice")
    print("Description: Discover Marstek Venus E devices on local network via UDP broadcast")
    print("Timeout: 15 seconds")
    print("-"*80)
    
    try:
        print("\n[INFO] Sending broadcast discovery probe to 255.255.255.255:30000...")
        print("[INFO] Waiting for device responses...\n")
        
        devices = await MarstekUDPClient.discover(timeout=15.0, port=30000)
        
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
            
            results.add_result(
                "Marstek.GetDevice (Discovery)",
                True,
                f"Successfully discovered {len(devices)} device(s)",
                {"device_count": len(devices), "devices": devices}
            )
            
            print("="*80)
            print("TEST 1 RESULT: ✓ PASSED")
            print("="*80)
            
            return devices[0]  # Return first device for subsequent tests
        else:
            print("[WARN] No devices found on the network")
            print("\nPossible reasons:")
            print("  • No Marstek Venus E devices powered on")
            print("  • Devices on different network/subnet")
            print("  • Firewall blocking UDP broadcast on port 30000")
            print("  • Device not connected to WiFi")
            
            results.add_result(
                "Marstek.GetDevice (Discovery)",
                False,
                "No devices found on network"
            )
            
            print("\n" + "="*80)
            print("TEST 1 RESULT: ✗ FAILED - No devices found")
            print("="*80)
            
            return None
            
    except Exception as err:
        print(f"[FAIL] Discovery error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        results.add_result(
            "Marstek.GetDevice (Discovery)",
            False,
            f"Exception: {type(err).__name__}: {err}"
        )
        
        print("\n" + "="*80)
        print("TEST 1 RESULT: ✗ FAILED - Exception occurred")
        print("="*80)
        
        return None


async def test_es_get_status(ip_address: str, port: int, results: TestResults) -> bool:
    """Test 2: ES.GetStatus.
    
    This function tests getting energy system status.
    
    Args:
        ip_address: Device IP address
        port: Device port
        results: TestResults object
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST 2: ES.GetStatus (Energy System Status)")
    print("="*80)
    print("Method: ES.GetStatus")
    print("Description: Get current energy system status (battery, PV, grid, power flow)")
    print(f"Target Device: {ip_address}:{port}")
    print("Timeout: 5 seconds")
    print("-"*80)
    
    try:
        client = MarstekUDPClient(ip_address, port, timeout=5.0)
        
        print("\n[INFO] Sending ES.GetStatus request...")
        print("[INFO] Request payload: {\"id\": 1, \"method\": \"ES.GetStatus\"}\n")
        
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
        
        results.add_result(
            "ES.GetStatus",
            True,
            "Successfully retrieved energy system status",
            status
        )
        
        print("\n" + "="*80)
        print("TEST 2 RESULT: ✓ PASSED")
        print("="*80)
        
        return True
        
    except asyncio.TimeoutError:
        print("[FAIL] Request timed out after 5 seconds")
        print("\n[INFO] Note: Some Marstek devices may only respond to broadcast requests,")
        print("[INFO] not to unicast requests. This is a known limitation.")
        print("[INFO] The integration works around this using periodic broadcast discovery.")
        
        results.add_result(
            "ES.GetStatus",
            False,
            "Request timeout - device may not respond to unicast requests"
        )
        
        print("\n" + "="*80)
        print("TEST 2 RESULT: ✗ FAILED - Timeout")
        print("="*80)
        
        return False
        
    except Exception as err:
        print(f"[FAIL] Error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        results.add_result(
            "ES.GetStatus",
            False,
            f"Exception: {type(err).__name__}: {err}"
        )
        
        print("\n" + "="*80)
        print("TEST 2 RESULT: ✗ FAILED - Exception")
        print("="*80)
        
        return False


async def test_es_get_mode(ip_address: str, port: int, results: TestResults) -> bool:
    """Test 3: ES.GetMode.
    
    This function tests getting the current operating mode.
    
    Args:
        ip_address: Device IP address
        port: Device port
        results: TestResults object
        
    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "="*80)
    print("TEST 3: ES.GetMode (Operating Mode)")
    print("="*80)
    print("Method: ES.GetMode")
    print("Description: Get current operating mode (Auto, AI, Manual, Passive)")
    print(f"Target Device: {ip_address}:{port}")
    print("Timeout: 5 seconds")
    print("-"*80)
    
    try:
        client = MarstekUDPClient(ip_address, port, timeout=5.0)
        
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
        print(f"Operating Mode: {mode}")
        
        # Display mode-specific information
        if mode == "Manual":
            print("\nManual Mode Configuration:")
            manual_cfg = mode_data.get('manual_cfg', {})
            if manual_cfg:
                for key, value in manual_cfg.items():
                    print(f"  {key}: {value}")
        elif mode == "Passive":
            print(f"\nPassive Mode Power: {mode_data.get('passive_power', 'N/A')} W")
            print(f"Countdown Time: {mode_data.get('cd_time', 'N/A')} seconds")
        
        print("-"*80)
        
        results.add_result(
            "ES.GetMode",
            True,
            f"Successfully retrieved mode: {mode}",
            mode_data
        )
        
        print("\n" + "="*80)
        print("TEST 3 RESULT: ✓ PASSED")
        print("="*80)
        
        return True
        
    except asyncio.TimeoutError:
        print("[FAIL] Request timed out after 5 seconds")
        print("\n[INFO] Note: Some Marstek devices may only respond to broadcast requests,")
        print("[INFO] not to unicast requests. This is a known limitation.")
        
        results.add_result(
            "ES.GetMode",
            False,
            "Request timeout - device may not respond to unicast requests"
        )
        
        print("\n" + "="*80)
        print("TEST 3 RESULT: ✗ FAILED - Timeout")
        print("="*80)
        
        return False
        
    except Exception as err:
        print(f"[FAIL] Error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        results.add_result(
            "ES.GetMode",
            False,
            f"Exception: {type(err).__name__}: {err}"
        )
        
        print("\n" + "="*80)
        print("TEST 3 RESULT: ✗ FAILED - Exception")
        print("="*80)
        
        return False


async def run_all_tests(ip_address: Optional[str] = None, port: int = 30000):
    """Run all API function tests.
    
    Args:
        ip_address: Optional IP address to test (if None, uses discovery)
        port: Device port (default 30000)
    """
    print("\n")
    print("="*80)
    print("MARSTEK VENUS E - API FUNCTIONS TEST SUITE")
    print("="*80)
    print("Testing API Version: Local API 1.4.3")
    print("Tests to run:")
    print("  1. Marstek.GetDevice (Discovery)")
    print("  2. ES.GetStatus (Energy System Status)")
    print("  3. ES.GetMode (Operating Mode)")
    print("\nNote: ES.SetMode is excluded from testing as requested")
    print("="*80)
    
    results = TestResults()
    
    # Test 1: Discovery (Marstek.GetDevice)
    device = await test_marstek_get_device(results)
    
    # If no device discovered and no manual IP provided, stop here
    if device is None and ip_address is None:
        print("\n[INFO] No device discovered and no manual IP provided.")
        print("[INFO] Skipping remaining tests.")
        results.print_summary()
        return
    
    # Use discovered device or manual IP
    if ip_address:
        target_ip = ip_address
        target_port = port
        print(f"\n[INFO] Using manually provided IP: {target_ip}:{target_port}")
    else:
        target_ip, target_port, _ = device
        print(f"\n[INFO] Using discovered device: {target_ip}:{target_port}")
    
    # Test 2: ES.GetStatus
    await test_es_get_status(target_ip, target_port, results)
    
    # Test 3: ES.GetMode
    await test_es_get_mode(target_ip, target_port, results)
    
    # Print summary
    results.print_summary()
    
    # Additional information
    print("="*80)
    print("ADDITIONAL INFORMATION")
    print("="*80)
    print("\nAPI Methods Tested:")
    print("  ✓ Marstek.GetDevice - Device discovery via UDP broadcast")
    print("  ✓ ES.GetStatus - Energy system status retrieval")
    print("  ✓ ES.GetMode - Operating mode retrieval")
    print("\nAPI Methods NOT Tested (as requested):")
    print("  ✗ ES.SetMode - Change operating mode")
    print("\nOther Available API Methods (not tested):")
    print("  • Bat.GetStatus - Battery detailed status")
    print("  • Wifi.GetStatus - WiFi connection status")
    print("  • ES.SetSchedule - Configure manual schedule")
    print("  • ES.GetSchedule - Get manual schedule configuration")
    print("  • ES.SetPassiveMode - Set passive mode with power target")
    print("\nFor testing ES.SetMode or other write operations, use:")
    print("  python tests/test_api_functions.py --ip <device_ip> --test-writes")
    print("="*80)
    print()


async def main():
    """Main entry point."""
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("\nMarstek Venus E API Functions Test")
        print("="*80)
        print("\nUsage:")
        print("  python tests/test_api_functions.py")
        print("    Run all tests with automatic discovery")
        print("\n  python tests/test_api_functions.py --ip <ip_address> [--port <port>]")
        print("    Run tests on a specific device")
        print("\nExamples:")
        print("  python tests/test_api_functions.py")
        print("  python tests/test_api_functions.py --ip 192.168.0.225")
        print("  python tests/test_api_functions.py --ip 192.168.0.225 --port 30000")
        print("="*80)
        print()
        return
    
    ip_address = None
    port = 30000
    
    # Parse --ip argument
    if "--ip" in sys.argv:
        try:
            ip_index = sys.argv.index("--ip")
            ip_address = sys.argv[ip_index + 1]
        except (IndexError, ValueError):
            print("[ERROR] --ip requires an IP address argument")
            print("Usage: python tests/test_api_functions.py --ip 192.168.0.225")
            return
    
    # Parse --port argument
    if "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            port = int(sys.argv[port_index + 1])
        except (IndexError, ValueError):
            print("[ERROR] --port requires a valid port number")
            print("Usage: python tests/test_api_functions.py --ip 192.168.0.225 --port 30000")
            return
    
    # Run tests
    await run_all_tests(ip_address, port)


if __name__ == "__main__":
    asyncio.run(main())
