"""Test script to examine ES.GetSchedule response structure."""
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


async def test_get_schedule(ip_address: str, port: int = 30000):
    """Test ES.GetSchedule to understand schedule configuration structure.
    
    Args:
        ip_address: Device IP address
        port: UDP port (default 30000)
    """
    print("=" * 70)
    print("MARSTEK VENUS E - ES.GetSchedule TEST")
    print("=" * 70)
    print(f"\nDevice: {ip_address}:{port}\n")
    
    client = MarstekUDPClient(ip_address=ip_address, port=port, timeout=5.0)
    
    try:
        print("Sending ES.GetSchedule request...")
        print("-" * 70)
        
        schedule_data = await client.get_schedule()
        
        print("\n✓ SUCCESS - Received schedule configuration\n")
        print("=" * 70)
        print("COMPLETE RESPONSE (Formatted JSON):")
        print("=" * 70)
        print(json.dumps(schedule_data, indent=2, ensure_ascii=False))
        print()
        
        # Analyze the structure
        print("=" * 70)
        print("ANALYSIS:")
        print("=" * 70)
        
        # Look for schedule array
        schedule_array = None
        if "manual_cfg" in schedule_data:
            schedule_array = schedule_data["manual_cfg"]
            print(f"\n📋 Manual Configuration (manual_cfg):")
        elif "schedules" in schedule_data:
            schedule_array = schedule_data["schedules"]
            print(f"\n📋 Schedules (schedules):")
        elif isinstance(schedule_data, list):
            schedule_array = schedule_data
            print(f"\n📋 Schedule Array (root level):")
        
        if schedule_array and isinstance(schedule_array, list):
            print(f"   Type: list")
            print(f"   Number of schedules: {len(schedule_array)}")
            print()
            
            for idx, schedule in enumerate(schedule_array, 1):
                enabled = schedule.get("enable", False)
                status = "✓ ENABLED" if enabled else "✗ DISABLED"
                
                print(f"   Schedule #{idx} [{status}]:")
                for key, value in schedule.items():
                    if key == "week_set":
                        days = decode_week_set(value)
                        print(f"      {key}: {value} → {days}")
                    elif key == "power":
                        action = "CHARGE" if value < 0 else "DISCHARGE" if value > 0 else "IDLE"
                        print(f"      {key}: {value}W → {action}")
                    else:
                        print(f"      {key}: {value}")
                print()
        
        # Other fields
        other_fields = {k: v for k, v in schedule_data.items() 
                       if k not in ["manual_cfg", "schedules"] and not isinstance(schedule_data, list)}
        if other_fields:
            print(f"\n📝 Other Fields:")
            for key, value in other_fields.items():
                print(f"   {key}: {value}")
        
        # Detailed breakdown
        if schedule_array and isinstance(schedule_array, list):
            print("\n" + "=" * 70)
            print("DETAILED SCHEDULE BREAKDOWN:")
            print("=" * 70)
            
            for idx, schedule in enumerate(schedule_array, 1):
                enabled = schedule.get("enable", False)
                status = "✓ ENABLED" if enabled else "✗ DISABLED"
                
                print(f"\n🕐 Time Slot {idx} [{status}]")
                
                # Time range
                start = schedule.get("start_time", "N/A")
                end = schedule.get("end_time", "N/A")
                print(f"   └─ Time Range: {start} → {end}")
                
                # Decode week_set
                week_set = schedule.get("week_set", 0)
                days = decode_week_set(week_set)
                print(f"   └─ Active Days: {days}")
                print(f"      (Bitmask: {week_set} = {format_bitmask(week_set)})")
                
                # Power interpretation
                power = schedule.get("power", 0)
                if power < 0:
                    action = f"CHARGE battery at {abs(power)}W"
                elif power > 0:
                    action = f"DISCHARGE battery at {power}W"
                else:
                    action = "IDLE - No charging or discharging"
                print(f"   └─ Power: {power}W")
                print(f"      Action: {action}")
                
                # Calculate daily energy
                if start != "N/A" and end != "N/A" and power != 0:
                    duration = calculate_duration(start, end)
                    energy_wh = abs(power) * duration
                    energy_kwh = energy_wh / 1000
                    print(f"      Duration: {duration:.1f}h → {energy_kwh:.2f}kWh per day")
                
                # Other fields in schedule
                other = {k: v for k, v in schedule.items() 
                        if k not in ["enable", "start_time", "end_time", "week_set", "power"]}
                if other:
                    print(f"   └─ Additional: {other}")
        
        print("\n" + "=" * 70)
        print("SUMMARY:")
        print("=" * 70)
        
        if schedule_array and isinstance(schedule_array, list):
            active_count = sum(1 for s in schedule_array if s.get("enable", False))
            print(f"\n• Total Schedules: {len(schedule_array)}")
            print(f"• Active Schedules: {active_count}")
            print(f"• Inactive Schedules: {len(schedule_array) - active_count}")
            
            # Summary of active schedules
            if active_count > 0:
                print(f"\nActive Schedule Times:")
                for idx, schedule in enumerate(schedule_array, 1):
                    if schedule.get("enable", False):
                        start = schedule.get("start_time", "?")
                        end = schedule.get("end_time", "?")
                        power = schedule.get("power", 0)
                        action = "Charge" if power < 0 else "Discharge"
                        print(f"  Slot {idx}: {start}-{end}, {action} {abs(power)}W")
        
    except asyncio.TimeoutError:
        print("\n✗ TIMEOUT - No response from device")
        print("  Possible causes:")
        print("  - Device not reachable")
        print("  - Network/firewall blocking UDP")
        print("  - Device might not support ES.GetSchedule method")
        
    except Exception as err:
        print(f"\n✗ ERROR: {err}")
        import traceback
        traceback.print_exc()


def decode_week_set(week_set: int) -> str:
    """Decode week_set bitmask to readable day names."""
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
    
    if week_set == 31:
        result += " (Weekdays)"
    elif week_set == 96:
        result += " (Weekend)"
    
    return result


def format_bitmask(value: int) -> str:
    """Format bitmask as binary with labels."""
    binary = format(value, '07b')
    return f"{binary} (Sun Sat Fri Thu Wed Tue Mon)"


def calculate_duration(start_time: str, end_time: str) -> float:
    """Calculate duration in hours between two times."""
    try:
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))
        
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        # Handle overnight schedules
        if end_minutes < start_minutes:
            end_minutes += 24 * 60
        
        duration_minutes = end_minutes - start_minutes
        return duration_minutes / 60.0
    except:
        return 0.0


async def main():
    """Run the test."""
    if len(sys.argv) < 2:
        print("Usage: python test_get_schedule.py <device_ip> [port]")
        print("Example: python test_get_schedule.py 192.168.0.225")
        print("Example: python test_get_schedule.py 192.168.0.225 30000")
        return
    
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
    
    await test_get_schedule(ip, port)


if __name__ == "__main__":
    asyncio.run(main())
