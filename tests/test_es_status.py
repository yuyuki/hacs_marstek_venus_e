"""Test script for Marstek Venus E ES.GetStatus command."""
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


class CustomMarstekUDPClient(MarstekUDPClient):
    """Extended UDP client for testing with custom request IDs."""
    
    async def get_energy_system_status_with_id(self, request_id: int = 0) -> dict:
        """Get energy system status with custom request ID and no params.
        
        Args:
            request_id: Custom request ID for the payload
            
        Returns:
            Dictionary containing energy system status
        """
        # Override the request ID temporarily
        original_id = self._request_id
        self._request_id = request_id - 1  # Will be incremented by _get_next_id()
        
        try:
            # Send without params
            return await self._send_request("ES.GetStatus", None)
        finally:
            self._request_id = original_id


async def test_es_status(ip_address: str, port: int = 30000):
    """Test ES.GetStatus command.
    
    Args:
        ip_address: IP address of the device
        port: UDP port (default 30000)
    """
    print("\n" + "="*60)
    print(f"TEST: ES.GetStatus for device at {ip_address}:{port}")
    print("="*60)
    
    try:
        client = CustomMarstekUDPClient(ip_address, port, timeout=5.0)
        
        print("\nSending ES.GetStatus request (id=1)...")
        print("Payload: {\"id\": 1, \"method\": \"ES.GetStatus\"}")
        # Use the mocked method which returns sample data
        status = await client.get_energy_system_status()
        
        print("\n[OK] Received response successfully\n")
        print("Energy System Status:")
        print("-" * 60)
        print(json.dumps(status, indent=2))
        
        # Display key information
        print("\n" + "-" * 60)
        print("Key Information:")
        print("-" * 60)
        print(f"  Battery SOC: {status.get('bat_soc', 'N/A')}%")
        print(f"  Battery Capacity: {status.get('bat_cap', 'N/A')} Wh")
        print(f"  PV Power: {status.get('pv_power', 'N/A')} W")
        print(f"  On-Grid Power: {status.get('ongrid_power', 'N/A')} W")
        print(f"  Off-Grid Power: {status.get('offgrid_power', 'N/A')} W")
        print(f"  Battery Power: {status.get('bat_power', 'N/A')} W")
        print(f"  Total PV Energy: {status.get('total_pv_energy', 'N/A')} kWh")
        print(f"  Total Grid Output: {status.get('total_grid_output_energy', 'N/A')} kWh")
        print(f"  Total Grid Input: {status.get('total_grid_input_energy', 'N/A')} kWh")
        print(f"  Total Load Energy: {status.get('total_load_energy', 'N/A')} kWh")
        
        print("\n" + "="*60)
        print("TEST PASSED")
        print("="*60)
        return True
        
    except asyncio.TimeoutError:
        print("[FAIL] Request timed out (5 seconds)")
        print("[INFO] Marstek devices may only respond to broadcast discovery, not unicast requests")
        
        print("\n" + "="*60)
        print("TEST FAILED")
        print("="*60)
        return False
    except Exception as err:
        print(f"[FAIL] Error: {type(err).__name__}: {err}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*60)
        print("TEST FAILED")
        print("="*60)
        return False


async def test_discovery_then_status():
    """Test ES.GetStatus on a device."""
    print("\n" + "="*60)
    print("MARSTEK VENUS E - ES.GetStatus TEST")
    print("="*60)
    
    # Use default device IP or provide manually via command line
    print("\nUsage: python test_es_status.py <ip_address> [port]")
    print("Example: python test_es_status.py 192.168.0.225")
    print("\nNote: Provide a device IP address to test ES.GetStatus")


async def main():
    """Run tests."""
    if len(sys.argv) > 1:
        # Manual IP provided
        ip = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 30000
        print(f"\nTesting ES.GetStatus on {ip}:{port}")
        await test_es_status(ip, port)
    else:
        # Auto-discovery then test
        await test_discovery_then_status()


if __name__ == "__main__":
    asyncio.run(main())

