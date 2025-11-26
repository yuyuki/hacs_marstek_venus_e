"""Comprehensive test of all available API methods."""
import asyncio
import json
import sys
import importlib.util
from pathlib import Path

# Setup path to load udp_client module
udp_client_path = Path(__file__).parent.parent / "custom_components" / "hacs_marstek_venus_e" / "udp_client.py"
spec = importlib.util.spec_from_file_location("udp_client", udp_client_path)
udp_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(udp_client_module)

MarstekUDPClient = udp_client_module.MarstekUDPClient


async def test_all_methods(ip_address: str, port: int = 30000):
    """Test all available API methods to see complete data structure.
    
    Args:
        ip_address: Device IP address
        port: UDP port (default 30000)
    """
    print("=" * 80)
    print("MARSTEK VENUS E - COMPREHENSIVE API TEST")
    print("=" * 80)
    print(f"\nDevice: {ip_address}:{port}")
    print(f"Testing all known API methods...\n")
    
    client = MarstekUDPClient(ip_address=ip_address, port=port, timeout=5.0)
    
    # List of methods to test
    methods = [
        ("ES.GetMode", "ES.GetMode", {"id": 0}),
        ("ES.GetStatus", "ES.GetStatus", {"id": 0}),
        ("Bat.GetStatus", "Bat.GetStatus", {"id": 0}),
        ("Marstek.GetDevice", "Marstek.GetDevice", {"ble_mac": "0"}),
        ("Wifi.GetStatus", "Wifi.GetStatus", {"id": 0}),
    ]
    
    results = {}
    
    for name, method, params in methods:
        print("=" * 80)
        print(f"Testing: {name}")
        print("=" * 80)
        
        try:
            response = await client._send_request(method, params)
            results[name] = response
            
            print(f"✓ SUCCESS\n")
            print(json.dumps(response, indent=2, ensure_ascii=False))
            print()
            
        except asyncio.TimeoutError:
            print(f"✗ TIMEOUT - No response\n")
            results[name] = None
            
        except Exception as err:
            print(f"✗ ERROR: {err}\n")
            results[name] = None
    
    # Summary and analysis
    print("\n" + "=" * 80)
    print("SUMMARY & ANALYSIS")
    print("=" * 80)
    
    # Analyze ES.GetMode
    if results.get("ES.GetMode"):
        print("\n📌 ES.GetMode - Current Operating Mode")
        print("-" * 80)
        mode_data = results["ES.GetMode"]
        print(f"  Current Mode: {mode_data.get('mode', 'Unknown')}")
        print(f"  Battery SOC: {mode_data.get('bat_soc', 'N/A')}%")
        print(f"  On-Grid Power: {mode_data.get('ongrid_power', 'N/A')}W")
        print(f"  Off-Grid Power: {mode_data.get('offgrid_power', 'N/A')}W")
        
        # Check for schedule info
        if "manual_cfg" in mode_data:
            print(f"  Manual Config: Present")
        else:
            print(f"  ⚠ Manual Config: NOT in ES.GetMode response")
    
    # Analyze ES.GetStatus
    if results.get("ES.GetStatus"):
        print("\n⚡ ES.GetStatus - Energy System Status")
        print("-" * 80)
        es_data = results["ES.GetStatus"]
        
        # Look for mode-related fields
        mode_fields = ["mode", "manual_cfg", "ai_cfg", "passive_cfg", "schedule", "schedules"]
        found_mode_fields = {k: v for k, v in es_data.items() if k in mode_fields}
        
        if found_mode_fields:
            print("  Mode-related fields found:")
            for key, value in found_mode_fields.items():
                if isinstance(value, (list, dict)):
                    print(f"    {key}: {type(value).__name__} with {len(value)} items")
                else:
                    print(f"    {key}: {value}")
        else:
            print("  ⚠ No mode configuration fields in ES.GetStatus")
        
        # Show key status fields
        key_fields = ["bat_power", "pv_power", "grid_power", "load_power", "bat_soc"]
        print("\n  Key Status Fields:")
        for field in key_fields:
            if field in es_data:
                print(f"    {field}: {es_data[field]}")
    
    # Analyze Battery Status
    if results.get("Bat.GetStatus"):
        print("\n🔋 Bat.GetStatus - Battery Information")
        print("-" * 80)
        bat_data = results["Bat.GetStatus"]
        
        key_fields = ["bat_soc", "bat_temp", "bat_capacity", "bat_voltage", "bat_current"]
        for field in key_fields:
            if field in bat_data:
                print(f"  {field}: {bat_data[field]}")
    
    print("\n" + "=" * 80)
    print("KEY FINDINGS:")
    print("=" * 80)
    
    mode_data = results.get("ES.GetMode", {})
    es_data = results.get("ES.GetStatus", {})
    
    print("""
Based on the API responses:

1. ES.GetMode returns:
   - Current mode (Auto/AI/Manual/Passive)
   - Current battery SOC
   - Power values
   BUT: Does NOT include manual_cfg schedule configuration

2. ES.GetStatus returns:
   - Real-time energy system data
   - Battery, PV, Grid, Load power values
   Check if it contains schedule configuration...

3. Manual schedules might be:
   - Stored locally on device without API access
   - Accessible through different method name
   - Part of device firmware internal state
    """)
    
    # Check all fields across all responses for schedule-related data
    print("\n" + "=" * 80)
    print("SEARCHING FOR SCHEDULE DATA IN ALL RESPONSES:")
    print("=" * 80)
    
    schedule_keywords = ["schedule", "manual", "time", "cfg", "config"]
    
    for method_name, response_data in results.items():
        if response_data:
            print(f"\n{method_name}:")
            matching_fields = []
            
            for key in response_data.keys():
                if any(keyword in key.lower() for keyword in schedule_keywords):
                    matching_fields.append(key)
            
            if matching_fields:
                print(f"  Found: {', '.join(matching_fields)}")
                for field in matching_fields:
                    value = response_data[field]
                    if isinstance(value, (list, dict)):
                        print(f"    {field}: {json.dumps(value, indent=6, ensure_ascii=False)}")
                    else:
                        print(f"    {field}: {value}")
            else:
                print(f"  No schedule-related fields")


async def main():
    """Run the comprehensive test."""
    if len(sys.argv) < 2:
        print("Usage: python test_all_methods.py <device_ip> [port]")
        print("Example: python test_all_methods.py 192.168.0.225")
        return
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    
    await test_all_methods(ip, port)


if __name__ == "__main__":
    asyncio.run(main())
