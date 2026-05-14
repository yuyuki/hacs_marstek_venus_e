"""Deterministic tests for Marstek discovery broadcast target generation."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


UDP_CLIENT_PATH = Path(__file__).parent.parent / "custom_components" / "hacs_marstek_venus_e" / "udp_client.py"
CONST_PATH = Path(__file__).parent.parent / "custom_components" / "hacs_marstek_venus_e" / "const.py"


def load_module_from_file(module_name: str, file_path: Path):
    """Load a module from disk using the same pattern as the existing test scripts."""

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


load_module_from_file(
    "custom_components.hacs_marstek_venus_e.const",
    CONST_PATH,
)
UDP_CLIENT_MODULE = load_module_from_file(
    "custom_components.hacs_marstek_venus_e.udp_client",
    UDP_CLIENT_PATH,
)

MarstekUDPClient = UDP_CLIENT_MODULE.MarstekUDPClient


class FakeSocket:
    """Minimal socket stub for discovery helper tests."""

    def __init__(self, *args, **kwargs):
        self._closed = False
        self._connected = False

    def connect(self, address):
        self._connected = True

    def getsockname(self):
        return ("192.168.1.42", 12345)

    def close(self):
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


class DiscoveryTargetTests(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_gethostbyname_ex = UDP_CLIENT_MODULE.socket.gethostbyname_ex
        self._orig_socket = UDP_CLIENT_MODULE.socket.socket

    def tearDown(self) -> None:
        UDP_CLIENT_MODULE.socket.gethostbyname_ex = self._orig_gethostbyname_ex
        UDP_CLIENT_MODULE.socket.socket = self._orig_socket

    def test_local_ipv4_addresses_are_deduped(self) -> None:
        UDP_CLIENT_MODULE.socket.gethostbyname_ex = lambda hostname: (
            hostname,
            [],
            ["127.0.0.1", "192.168.1.42", "192.168.1.42", "10.0.0.15"],
        )
        UDP_CLIENT_MODULE.socket.socket = lambda *args, **kwargs: FakeSocket()

        addresses = MarstekUDPClient._get_local_ipv4_addresses()

        self.assertEqual(addresses, ["192.168.1.42", "10.0.0.15"])

    def test_discovery_targets_include_common_broadcasts(self) -> None:
        UDP_CLIENT_MODULE.socket.gethostbyname_ex = lambda hostname: (
            hostname,
            [],
            ["192.168.1.42"],
        )
        UDP_CLIENT_MODULE.socket.socket = lambda *args, **kwargs: FakeSocket()

        targets = MarstekUDPClient._get_discovery_targets(30000)

        self.assertEqual(targets[0], ("255.255.255.255", 30000))
        self.assertIn(("192.168.1.255", 30000), targets)
        self.assertIn(("192.168.255.255", 30000), targets)


if __name__ == "__main__":
    unittest.main()
