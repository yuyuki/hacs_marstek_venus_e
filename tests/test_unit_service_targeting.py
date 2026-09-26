"""Device-free checks for multi-battery targeting and failure reporting."""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


source = Path(__file__).resolve().parents[1] / "custom_components/hacs_marstek_venus_e/services.py"
tree = ast.parse(source.read_text())
functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name in ("_target_coordinators", "_execute_targeted")]
module = ast.Module(body=functions, type_ignores=[])
namespace = {"DOMAIN": "hacs_marstek_venus_e", "_LOGGER": Mock(),
             "HomeAssistant": object, "ServiceCall": object}


class EntityRegistry:
    def __init__(self):
        self.entities = {
            "sensor.first": SimpleNamespace(config_entry_id="first", area_id="kitchen"),
            "sensor.second": SimpleNamespace(config_entry_id="second", area_id=None),
        }

    def async_get(self, entity_id):
        return self.entities.get(entity_id)


class DeviceRegistry:
    def __init__(self):
        self.devices = {
            "dev-first": SimpleNamespace(config_entries={"first"}),
            "dev-second": SimpleNamespace(config_entries={"second"}),
        }

    def async_get(self, device_id):
        return self.devices.get(device_id)


namespace["er"] = SimpleNamespace(async_get=lambda hass: hass.entities)
namespace["dr"] = SimpleNamespace(
    async_get=lambda hass: hass.devices,
    async_entries_for_area=lambda registry, area: [registry.devices["dev-second"]] if area == "garage" else [],
)
exec(compile(module, str(source), "exec"), namespace)


class ServiceTargetTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.first = Mock()
        self.second = Mock()
        self.hass = SimpleNamespace(
            data={namespace["DOMAIN"]: {"first": self.first, "second": self.second}},
            entities=EntityRegistry(), devices=DeviceRegistry(),
        )

    def test_device_and_entity_targets(self):
        select = namespace["_target_coordinators"]
        self.assertEqual(select(self.hass, {"device_id": ["dev-first"]}), {"first": self.first})
        self.assertEqual(select(self.hass, {"entity_id": ["sensor.second"]}), {"second": self.second})
        self.assertEqual(select(self.hass, {"area_id": ["garage"]}), {"second": self.second})
        self.assertEqual(len(select(self.hass, {})), 2)
        with self.assertRaisesRegex(ValueError, "No Marstek"):
            select(self.hass, {"device_id": ["unknown"]})

    async def test_partial_failure_is_reported_per_battery(self):
        async def operation(coordinator):
            if coordinator is self.second:
                raise TimeoutError("battery timed out")

        call = SimpleNamespace(data={}, return_response=True)
        result = await namespace["_execute_targeted"](self.hass, call, operation)
        self.assertEqual(result["results"]["first"], {"ok": True})
        self.assertEqual(result["results"]["second"]["ok"], False)

        call.return_response = False
        with self.assertRaisesRegex(ValueError, "battery timed out"):
            await namespace["_execute_targeted"](self.hass, call, operation)


if __name__ == "__main__":
    unittest.main()
