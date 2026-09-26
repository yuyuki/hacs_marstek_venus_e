"""Device-free tests for UDP reliability and the revision 3.1 write shape."""
import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


PACKAGE = "marstek_unit"
package = types.ModuleType(PACKAGE)
package.__path__ = []
sys.modules[PACKAGE] = package
constants = types.ModuleType(f"{PACKAGE}.const")
constants.DEFAULT_TIMEOUT = 30.0
sys.modules[constants.__name__] = constants
path = Path(__file__).resolve().parents[1] / "custom_components/hacs_marstek_venus_e/udp_client.py"
spec = importlib.util.spec_from_file_location(f"{PACKAGE}.udp_client", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
MarstekUDPClient = module.MarstekUDPClient


class UDPClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_timeout_retries_and_closes_each_transport(self):
        client = MarstekUDPClient("192.0.2.10", timeout=0.01)
        transports = []

        async def endpoint(factory, remote_addr):
            transport = unittest.mock.Mock()
            protocol = factory()
            protocol.get_response = AsyncMock(side_effect=asyncio.TimeoutError)
            transports.append(transport)
            return transport, protocol

        with patch.object(asyncio.get_running_loop(), "create_datagram_endpoint", side_effect=endpoint):
            with self.assertRaises(asyncio.TimeoutError):
                await client.get_energy_system_status()

        self.assertEqual(len(transports), 2)
        for transport in transports:
            transport.sendto.assert_called_once()
            transport.close.assert_called_once()

    async def test_manual_slot_uses_only_documented_set_mode(self):
        client = MarstekUDPClient("192.0.2.10")
        client._send_request = AsyncMock(return_value={"set_result": True})

        await client.set_manual_schedule(2, "09:00", "10:00", 127, -500)

        client._send_request.assert_awaited_once_with(
            "ES.SetMode",
            {"id": 0, "config": {"mode": "Manual", "manual_cfg": {
                "time_num": 2, "start_time": "09:00", "end_time": "10:00",
                "week_set": 127, "power": -500, "enable": 1,
            }}},
        )

    async def test_rejected_write_is_error(self):
        client = MarstekUDPClient("192.0.2.10")
        client._send_request = AsyncMock(return_value={"set_result": False})
        with self.assertRaisesRegex(ValueError, "not acknowledged"):
            await client.set_passive_mode(400)

    async def test_firmware_response_id_one_is_accepted(self):
        protocol = module._UDPClientProtocol(expected_id=0)
        protocol.datagram_received(json.dumps({"id": 1, "result": {"set_result": True}}).encode(),
                                   ("192.0.2.10", 30000))
        self.assertEqual(await protocol.get_response(), {"id": 1, "result": {"set_result": True}})

    async def test_concurrent_requests_to_one_device_are_serialized(self):
        client = MarstekUDPClient("192.0.2.10")
        entered = asyncio.Event()
        release = asyncio.Event()
        order = []

        async def operation(method, params):
            order.append(f"start {method}")
            if method == "first":
                entered.set()
                await release.wait()
            order.append(f"end {method}")
            return {}

        client._send_request_locked = operation
        first = asyncio.create_task(client._send_request("first"))
        await entered.wait()
        second = asyncio.create_task(client._send_request("second"))
        await asyncio.sleep(0)
        self.assertEqual(order, ["start first"])
        release.set()
        await asyncio.gather(first, second)
        self.assertEqual(order, ["start first", "end first", "start second", "end second"])


if __name__ == "__main__":
    unittest.main()
