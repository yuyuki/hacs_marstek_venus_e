"""Test script to examine ES.GetMode response structure."""
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


async def test_get_mode(ip_address: str, port: int = 30000):
    """Test ES.GetMode to understand mode configuration structure.
    
    Args:
        ip_address: Device IP address
        port: UDP port (default 30000)
    """
    print("=" * 70)
    print("MARSTEK VENUS E - ES.GetMode TEST")
    print("=" * 70)
    print(f"\nDevice: {ip_address}:{port}")
    print(f"Current Mode: Manual (as you set it)\n")
    
    client = MarstekUDPClient(ip_address=ip_address, port=port, timeout=5.0)
    
    try:
        print("Sending ES.GetMode request...")
        print("-" * 70)
        
        mode_data = await client.get_energy_system_mode()
        
        print("\n✓ SUCCESS - Received mode configuration\n")
        print("=" * 70)
        print("COMPLETE RESPONSE (Formatted JSON):")
        print("=" * 70)
        print(json.dumps(mode_data, indent=2, ensure_ascii=False))
        print()
        
        # Analyze the structure
        print("=" * 70)
        print("ANALYSIS:")
        print("=" * 70)
        
        # Current mode
        if "mode" in mode_data:
            print(f"\n📌 Current Mode: {mode_data['mode']}")
        
        # Manual configuration
        if "manual_cfg" in mode_data:
            manual_cfg = mode_data["manual_cfg"]
            print(f"\n📋 Manual Configuration Found:")
            print(f"   Type: {type(manual_cfg)}")
            
            if isinstance(manual_cfg, list):
                print(f"   Number of schedules: {len(manual_cfg)}")
                print()
                
                for idx, schedule in enumerate(manual_cfg, 1):
                    print(f"   Schedule #{idx}:")
                    for key, value in schedule.items():
                        print(f"      {key}: {value}")
                    print()
            else:
                print(f"   Data: {manual_cfg}")
        
        # AI configuration
        if "ai_cfg" in mode_data:
            print(f"\n🤖 AI Configuration: {mode_data['ai_cfg']}")
        
        # Passive configuration  
        if "passive_cfg" in mode_data:
            print(f"\n⚡ Passive Configuration: {mode_data['passive_cfg']}")
        
        # Other fields
        other_fields = {k: v for k, v in mode_data.items() 
                       if k not in ["mode", "manual_cfg", "ai_cfg", "passive_cfg"]}
        if other_fields:
            print(f"\n📝 Other Fields:")
            for key, value in other_fields.items():
                print(f"   {key}: {value}")
        
        # Detailed schedule breakdown
        if "manual_cfg" in mode_data and isinstance(mode_data["manual_cfg"], list):
            print("\n" + "=" * 70)
            print("DETAILED SCHEDULE BREAKDOWN:")
            print("=" * 70)
            
            for idx, schedule in enumerate(mode_data["manual_cfg"], 1):
                enabled = schedule.get("enable", False)
                status = "✓ ENABLED" if enabled else "✗ DISABLED"
                
                print(f"\n🕐 Time Slot {idx} [{status}]")
                print(f"   └─ Time Range: {schedule.get('start_time', 'N/A')} → {schedule.get('end_time', 'N/A')}")
                
                # Decode week_set
                week_set = schedule.get("week_set", 0)
                days = decode_week_set(week_set)
                print(f"   └─ Active Days: {days} (bitmask: {week_set})")
                
                # Power interpretation
                power = schedule.get("power", 0)
                if power < 0:
                    action = f"CHARGE at {abs(power)}W"
                elif power > 0:
                    action = f"DISCHARGE at {power}W"
                else:
                    action = "IDLE (0W)"
                print(f"   └─ Power: {power}W → {action}")
                
                # Other fields in schedule
                other = {k: v for k, v in schedule.items() 
                        if k not in ["enable", "start_time", "end_time", "week_set", "power"]}
                if other:
                    print(f"   └─ Additional fields: {other}")
        
        print("\n" + "=" * 70)
        print("KEY INSIGHTS:")
        print("=" * 70)
        print("""
• Mode field: Current operating mode (Auto/AI/Manual/Passive)
• manual_cfg: Array of up to 4 time-based schedules
• Each schedule has:
  - enable: Boolean to activate/deactivate
  - start_time: "HH:MM" format
  - end_time: "HH:MM" format  
  - week_set: Bitmask for days (1=Mon, 2=Tue, 4=Wed, 8=Thu, 16=Fri, 32=Sat, 64=Sun)
  - power: Watts (negative=charge, positive=discharge)
        """)
        
    except asyncio.TimeoutError:
        print("\n✗ TIMEOUT - No response from device")
        print("  This may indicate:")
        print("  - Device is not reachable at this IP")
        print("  - Network/firewall blocking UDP")
        print("  - Device is off or disconnected")
        
    except Exception as err:
        print(f"\n✗ ERROR: {err}")
        import traceback
        traceback.print_exc()


def decode_week_set(week_set: int) -> str:
    """Decode week_set bitmask to readable day names.
    
    Args:
        week_set: Bitmask value
        
    Returns:
        String with day names
    """
    if week_set == 0:
        return "No days"
    if week_set == 127:
        return "Every day"
    
    days = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i, name in enumerate(day_names):
        if week_set & (1 << i):
            days.append(name)
    
    result = ", ".join(days)
    
    # Add helpful shortcuts
    if week_set == 31:  # Mon-Fri
        result += " (Weekdays)"
    elif week_set == 96:  # Sat-Sun
        result += " (Weekend)"
    
    return result


async def main():
    """Run the test."""
    if len(sys.argv) < 2:
        print("Usage: python test_get_mode.py <device_ip> [port]")
        print("Example: python test_get_mode.py 192.168.0.225")
        print("Example: python test_get_mode.py 192.168.0.225 30000")
        return
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    
    await test_get_mode(ip, port)


if __name__ == "__main__":
    asyncio.run(main())
