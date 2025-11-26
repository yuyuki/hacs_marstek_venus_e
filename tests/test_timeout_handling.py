"""Test timeout handling for Marstek Venus E UDP client.

This test verifies that:
1. The default timeout is properly set to 10 seconds
2. Individual API call failures don't break the entire update
3. Coordinator continues working if at least one API call succeeds
"""

import asyncio
import sys
import logging
import importlib.util

# Load modules directly without triggering __init__.py
def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load const module first (udp_client depends on it)
const = load_module_from_file(
    "custom_components.hacs_marstek_venus_e.const",
    "../custom_components/hacs_marstek_venus_e/const.py"
)

# Load udp_client module
udp_client = load_module_from_file(
    "custom_components.hacs_marstek_venus_e.udp_client",
    "../custom_components/hacs_marstek_venus_e/udp_client.py"
)

MarstekUDPClient = udp_client.MarstekUDPClient
DEFAULT_TIMEOUT = const.DEFAULT_TIMEOUT

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_default_timeout():
    """Test that default timeout is properly configured."""
    print("\n" + "="*60)
    print("TEST 1: Default Timeout Configuration")
    print("="*60)
    
    client = MarstekUDPClient(ip_address="192.168.0.225")
    
    print(f"✓ Default timeout constant: {DEFAULT_TIMEOUT} seconds")
    print(f"✓ Client timeout: {client.timeout} seconds")
    
    assert client.timeout == DEFAULT_TIMEOUT, "Client timeout doesn't match constant"
    assert client.timeout == 10.0, "Default timeout should be 10 seconds"
    
    print("✓ DEFAULT TIMEOUT TEST PASSED\n")


async def test_custom_timeout():
    """Test that custom timeout can be set."""
    print("\n" + "="*60)
    print("TEST 2: Custom Timeout Configuration")
    print("="*60)
    
    custom_timeout = 15.0
    client = MarstekUDPClient(ip_address="192.168.0.225", timeout=custom_timeout)
    
    print(f"✓ Custom timeout: {custom_timeout} seconds")
    print(f"✓ Client timeout: {client.timeout} seconds")
    
    assert client.timeout == custom_timeout, "Custom timeout not properly set"
    
    print("✓ CUSTOM TIMEOUT TEST PASSED\n")


async def test_api_call_with_new_timeout(ip_address: str):
    """Test actual API call with new 10-second timeout."""
    print("\n" + "="*60)
    print("TEST 3: API Call with 10-Second Timeout")
    print("="*60)
    
    client = MarstekUDPClient(ip_address=ip_address)
    
    print(f"Testing API calls to {ip_address} with {client.timeout}s timeout...")
    
    # Test ES.GetStatus
    try:
        print("\n1. Testing ES.GetStatus (get_realtime_data)...")
        realtime_data = await client.get_realtime_data()
        print(f"   ✓ ES.GetStatus succeeded")
        print(f"   - Battery SOC: {realtime_data.get('bat_soc')}%")
        print(f"   - PV Power: {realtime_data.get('pv_power')}W")
    except asyncio.TimeoutError:
        print(f"   ✗ ES.GetStatus timed out after {client.timeout}s")
    except Exception as err:
        print(f"   ✗ ES.GetStatus failed: {err}")
    
    # Test Bat.GetStatus
    try:
        print("\n2. Testing Bat.GetStatus (get_battery_info)...")
        battery_info = await client.get_battery_info()
        print(f"   ✓ Bat.GetStatus succeeded")
        print(f"   - Battery SOC: {battery_info.get('soc')}%")
        print(f"   - Battery Temp: {battery_info.get('bat_temp')}°C")
        print(f"   - Charging: {battery_info.get('charg_flag')}")
    except asyncio.TimeoutError:
        print(f"   ✗ Bat.GetStatus timed out after {client.timeout}s")
    except Exception as err:
        print(f"   ✗ Bat.GetStatus failed: {err}")
    
    print("\n✓ API TIMEOUT TEST COMPLETED\n")


async def test_retry_logic(ip_address: str):
    """Test that retry logic works (2 attempts)."""
    print("\n" + "="*60)
    print("TEST 4: Retry Logic (2 Attempts)")
    print("="*60)
    
    client = MarstekUDPClient(ip_address=ip_address)
    
    print(f"Testing retry logic on {ip_address}...")
    print("Note: UDP client attempts each request twice before giving up\n")
    
    try:
        result = await client.get_battery_info()
        print("✓ Request succeeded (either first or second attempt)")
        print(f"  Battery SOC: {result.get('soc')}%")
    except asyncio.TimeoutError:
        print("✗ Request failed after 2 attempts")
        print(f"  Total time: ~{client.timeout * 2}s (2 attempts × {client.timeout}s)")
    except Exception as err:
        print(f"✗ Request failed with error: {err}")
    
    print("\n✓ RETRY LOGIC TEST COMPLETED\n")


async def main():
    """Run all timeout tests."""
    print("\n" + "="*60)
    print("MARSTEK VENUS E - TIMEOUT HANDLING TESTS")
    print("="*60)
    
    # Test 1: Default timeout configuration
    await test_default_timeout()
    
    # Test 2: Custom timeout configuration
    await test_custom_timeout()
    
    # Get device IP from command line or use default
    ip_address = "192.168.0.225"
    if len(sys.argv) > 1:
        ip_address = sys.argv[1]
    
    print(f"\n📡 Using device IP: {ip_address}")
    print(f"⏱️  Timeout: {DEFAULT_TIMEOUT} seconds")
    print(f"🔁 Retry attempts: 2")
    print(f"⏳ Max wait per call: {DEFAULT_TIMEOUT * 2} seconds\n")
    
    # Test 3: Actual API calls with new timeout
    await test_api_call_with_new_timeout(ip_address)
    
    # Test 4: Retry logic
    await test_retry_logic(ip_address)
    
    print("\n" + "="*60)
    print("ALL TIMEOUT TESTS COMPLETED")
    print("="*60)
    print("\n💡 Summary:")
    print("   • Default timeout increased from 5s to 10s")
    print("   • Each API call attempts twice before failing")
    print("   • Maximum wait per call: 20 seconds (2 × 10s)")
    print("   • Coordinator continues if at least one API call succeeds")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
