"""UDP JSON-RPC client for Marstek Venus E."""
from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import socket
from typing import Any

from .const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class MarstekUDPClient:
    """UDP JSON-RPC client for communicating with Marstek Venus E device."""

    def __init__(self, ip_address: str, port: int = 30000, timeout: float = DEFAULT_TIMEOUT):
        """Initialize the UDP client.
        
        Args:
            ip_address: IP address of the device
            port: UDP port (default 30000)
            timeout: Request timeout in seconds (default from DEFAULT_TIMEOUT constant)
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout

    def _get_next_id(self) -> int:
        """Get next request ID.
        
        Note: Marstek device always responds with id: 0 regardless of request ID,
        so we always use 0 to avoid ID mismatch issues.
        """
        return 0

    async def _send_request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON-RPC request and get response.
        
        Args:
            method: RPC method name
            params: Optional parameters dictionary
            
        Returns:
            Response data dictionary
            
        Raises:
            asyncio.TimeoutError: If request times out
            Exception: If device returns error
        """
        request_id = self._get_next_id()
        
        # Marstek uses simplified JSON-RPC format (no jsonrpc field)
        payload = {
            "id": request_id,
            "method": method,
        }
        
        if params:
            payload["params"] = params
        
        _LOGGER.debug("Sending request to %s:%d: %s", self.ip_address, self.port, payload)
        
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                loop = asyncio.get_event_loop()
                transport, protocol = await asyncio.wait_for(
                    loop.create_datagram_endpoint(
                        lambda: _UDPClientProtocol(request_id),
                        remote_addr=(self.ip_address, self.port),
                    ),
                    timeout=self.timeout,
                )
                
                transport.sendto(json.dumps(payload).encode("utf-8"))
                _LOGGER.debug("Sent %s request to %s:%d with payload: %s", method, self.ip_address, self.port, payload)
                
                response = await asyncio.wait_for(
                    protocol.get_response(), timeout=self.timeout
                )
                
                transport.close()
                
                _LOGGER.debug("Received raw response from %s:%d: %s", self.ip_address, self.port, response)
                
                if "error" in response:
                    error = response.get("error", {})
                    error_msg = f"{error.get('message', 'Unknown error')} (code: {error.get('code')})"
                    _LOGGER.error("RPC Error from %s:%d: %s", self.ip_address, self.port, error_msg)
                    raise Exception(f"RPC Error: {error_msg}")
                
                result = response.get("result", {})
                _LOGGER.debug("Extracted result from %s:%d: %s", self.ip_address, self.port, result)
                return result
                
            except asyncio.TimeoutError:
                _LOGGER.warning(
                    "Timeout (attempt %d/%d) for method '%s' to %s:%d",
                    attempt,
                    max_attempts,
                    method,
                    self.ip_address,
                    self.port,
                )
                if attempt < max_attempts:
                    _LOGGER.debug("Retrying %s...", method)
                    try:
                        transport.close()
                    except Exception:
                        pass
                    continue
                _LOGGER.error("Request timeout to %s:%d for method %s", self.ip_address, self.port, method)
                raise
            except Exception as err:
                _LOGGER.error("Error communicating with %s:%d - %s", self.ip_address, self.port, err)
                raise

    async def get_device_info(self) -> dict[str, Any]:
        """Get device information.
        
        Returns:
            Dictionary containing device info
        """
        return await self._send_request("Marstek.GetDevice", {"ble_mac": "0"})

    async def get_battery_status(self) -> dict[str, Any]:
        """Get battery status.
        
        Returns:
            Dictionary containing battery status
        """
        return await self._send_request("Bat.GetStatus", {"id": 0})

    async def get_wifi_status(self) -> dict[str, Any]:
        """Get WiFi connection status.
        
        Returns:
            Dictionary containing WiFi status
        """
        return await self._send_request("Wifi.GetStatus", {"id": 0})

    async def get_energy_system_status(self) -> dict[str, Any]:
        """Get energy system status.
        
        Returns:
            Dictionary containing energy system status
        """
        return await self._send_request("ES.GetStatus", {"id": 0})

    async def get_energy_system_mode(self) -> dict[str, Any]:
        """Get operating mode and CT meter data.
        
        Returns:
            Dictionary containing mode information and CT meter data
        """
        return await self._send_request("ES.GetMode", {"id": 0})

    async def get_energy_meter_status(self) -> dict[str, Any]:
        """Get energy meter (CT) status.
        
        Returns:
            Dictionary containing energy meter status
        """
        return await self._send_request("EM.GetStatus", {"id": 0})

    async def get_schedule(self) -> dict[str, Any]:
        """Get manual schedule configuration.
        
        Returns:
            Dictionary containing schedule configuration
        """
        return await self._send_request("ES.GetSchedule", {"id": 0})

    async def set_schedule(self, schedules: list[dict[str, Any]]) -> dict[str, Any]:
        """Set complete manual schedule configuration.
        
        Args:
            schedules: List of schedule configurations for all slots
            
        Returns:
            Response from device
        """
        return await self._send_request("ES.SetSchedule", {"id": 0, "schedules": schedules})

    # Keep old methods for backwards compatibility
    async def get_realtime_data(self) -> dict[str, Any]:
        """Get real-time data from device (alias for get_energy_system_status).
        
        Returns:
            Dictionary containing real-time data
        """
        return await self.get_energy_system_status()

    async def get_battery_info(self) -> dict[str, Any]:
        """Get battery information (alias for get_battery_status).
        
        Returns:
            Dictionary containing battery info
        """
        return await self.get_battery_status()

    async def set_mode(
        self,
        mode: str,
        manual_cfg: dict[str, Any] | None = None,
        passive_cfg: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Set operating mode.
        
        Args:
            mode: Mode name (Auto, AI, Manual, Passive)
            manual_cfg: Manual mode configuration (for Manual mode)
                       Should contain: time_num, start_time, end_time, week_set, power, enable
            passive_cfg: Passive mode configuration (for Passive mode)
                        Should contain: power, cd_time, enable
            
        Returns:
            Response from device
        """
        # Build the config based on mode
        config = {"mode": mode}
        
        if mode == "Auto":
            config["auto_cfg"] = {"enable": 1}
        elif mode == "AI":
            config["ai_cfg"] = {"enable": 1}
        elif mode == "Manual":
            if manual_cfg is not None:
                config["manual_cfg"] = manual_cfg
            # If manual_cfg is None, don't add it (allows clearing schedules)
        elif mode == "Passive":
            if passive_cfg is not None:
                config["passive_cfg"] = passive_cfg
            # If passive_cfg is None, don't add it
        
        return await self._send_request("ES.SetMode", {"id": 0, "config": config})

    async def set_manual_schedule(
        self,
        time_num: int,
        start_time: str,
        end_time: str,
        week_set: int,
        power: int,
        enable: bool = True,
    ) -> dict[str, Any]:
        """Set manual charging/discharging schedule.

        This method configures a specific schedule slot by retrieving current schedules,
        modifying the specified slot, and sending the complete configuration.

        Args:
            time_num: Time slot number (0-9)
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            week_set: Week bitmask (1=Mon, 2=Tue, ..., 64=Sun, 127=All)
            power: Power in watts (negative=charge, positive=discharge)
            enable: Enable the schedule

        Returns:
            Response from device
        """
        try:
            # Get current schedule configuration
            current_config = await self.get_schedule()
            
            # Extract schedules array
            schedules = []
            if "schedules" in current_config:
                schedules = current_config["schedules"]
            elif "manual_cfg" in current_config and isinstance(current_config["manual_cfg"], list):
                schedules = current_config["manual_cfg"]
            elif isinstance(current_config, list):
                schedules = current_config
            
            # Ensure we have at least 10 slots (0-9)
            while len(schedules) < 10:
                schedules.append({
                    "time_num": len(schedules),
                    "start_time": "00:00",
                    "end_time": "00:00", 
                    "week_set": 0,
                    "power": 0,
                    "enable": 0
                })
            
            # Update the specific slot
            if 0 <= time_num < len(schedules):
                schedules[time_num] = {
                    "time_num": time_num,
                    "start_time": start_time,
                    "end_time": end_time,
                    "week_set": week_set,
                    "power": power,
                    "enable": 1 if enable else 0,
                }
            
            # Send complete schedule configuration
            result = await self.set_schedule(schedules)
            
            # Also set mode to Manual to ensure schedules take effect
            await self.set_mode("Manual")
            
            return result
            
        except Exception as err:
            _LOGGER.error("Failed to set manual schedule: %s", err)
            # Fallback to old method if new approach fails
            manual_cfg = {
                "time_num": time_num,
                "start_time": start_time,
                "end_time": end_time,
                "week_set": week_set,
                "power": power,
                "enable": 1 if enable else 0,
            }
            return await self.set_mode("Manual", manual_cfg=manual_cfg)

    async def set_passive_mode(self, power: int, cd_time: int = 0) -> dict[str, Any]:
        """Set passive mode with power target.
        
        Args:
            power: Target power in watts
            cd_time: Countdown time in seconds (0 = indefinite)

        Returns:
            Response from device
        """
        passive_cfg = {"power": power, "cd_time": cd_time}
        return await self.set_mode("Passive", passive_cfg=passive_cfg)

    async def clear_all_manual_schedules(self) -> dict[str, Any]:
        """Clear all manual schedules by disabling all time slots (0-9).

        Returns:
            Dictionary with results for each slot
        """
        results = {
            "success_count": 0,
            "failed_slots": [],
            "total_slots": 10,
        }

        # Disable each slot from 0 to 9
        for slot_num in range(10):
            manual_cfg = {
                "time_num": slot_num,
                "start_time": "00:00",
                "end_time": "23:59",
                "week_set": 127,
                "power": 100,
                "enable": 0,
            }

            try:
                response = await self.set_mode("Manual", manual_cfg=manual_cfg)

                if response.get("set_result"):
                    results["success_count"] += 1
                else:
                    results["failed_slots"].append(slot_num)

            except Exception as err:
                _LOGGER.error("Failed to disable slot %d: %s", slot_num, err)
                results["failed_slots"].append(slot_num)

        return results

    async def set_ble_adv(self, enable: bool) -> dict[str, Any]:
        """Control Bluetooth advertising.
        
        Args:
            enable: True to enable advertising, False to disable
            
        Returns:
            Response from device
        """
        enable_value = 0 if enable else 1  # 0 = enable, 1 = disable
        _LOGGER.debug("Setting Bluetooth advertising to %s", "enabled" if enable else "disabled")
        return await self._send_request("Ble.Adv", {"enable": enable_value})

    async def set_led_ctrl(self, enabled: bool) -> dict[str, Any]:
        """Control LED on the device panel.
        
        Args:
            enabled: True to turn LED on, False to turn off
            
        Returns:
            Response from device
        """
        state = 1 if enabled else 0
        _LOGGER.debug("Setting LED to %s", "on" if enabled else "off")
        return await self._send_request("Led.Ctrl", {"state": state})

    @staticmethod
    async def discover(timeout: float = 15.0, port: int = 30000) -> list[tuple[str, int, dict[str, Any]]]:
        """Discover Marstek devices on the local network via UDP broadcast.

        Sends a JSON-RPC discovery probe as a UDP broadcast and collects
        any JSON responses received within `timeout` seconds.

        Returns a list of tuples: (ip, port, parsed_json_response).
        Deduplicates responses by IP address and filters out invalid responses.
        """
        import time
        
        probe = {
            "id": 0,
            "method": "Marstek.GetDevice",
            "params": {
                "ble_mac": "0"
            }
        }
        
        probe_json = json.dumps(probe)
        probe_bytes = probe_json.encode("utf-8")
        
        # Create socket bound to the discovery port when possible. Some environments
        # already use the port, so we fall back to an ephemeral source port if bind fails.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        if hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
        try:
            # Bind to the discovery port so device responses are received
            sock.bind(("", port))
            _LOGGER.debug("Bound to UDP port %d for discovery responses", port)
        except OSError as err:
            _LOGGER.warning("Could not bind to UDP port %d: %s - discovery may fail", port, err)

        sock.settimeout(1.0)  # Short timeout for individual recv attempts

        local_ips = set(MarstekUDPClient._get_local_ipv4_addresses())
        broadcast_targets = MarstekUDPClient._get_discovery_targets(port, local_ips=local_ips)
        _LOGGER.debug("Discovery broadcast targets: %s", broadcast_targets)

        responses: dict[str, tuple[str, int, dict[str, Any]]] = {}
        start_time = time.time()
        last_broadcast = 0.0
        
        try:
            _LOGGER.debug("Starting discovery with probe: %s", probe)
            
            # Broadcast repeatedly every 2 seconds during the timeout window
            while time.time() - start_time < timeout:
                current_time = time.time()
                
                # Send broadcast every 2 seconds
                if current_time - last_broadcast >= 2.0:
                    try:
                        for target in broadcast_targets:
                            sock.sendto(probe_bytes, target)
                            _LOGGER.debug("Sent discovery probe to %s:%d", target[0], target[1])
                        last_broadcast = current_time
                    except Exception as exc_send:
                        _LOGGER.warning("Failed to send discovery probe: %s", exc_send)
                
                # Try to receive responses (non-blocking with timeout)
                try:
                    data, addr = sock.recvfrom(4096)
                    try:
                        text = data.decode("utf-8", errors="replace")
                        payload = json.loads(text)
                        
                        # Only keep valid responses with "result" field (filter out echoes)
                        result = payload.get("result", {})
                        if addr[0] in local_ips:
                            _LOGGER.debug("Ignoring discovery response from local address %s: %s", addr[0], payload)
                        elif isinstance(result, dict) and result:
                            ip_addr = str(result.get("ip") or addr[0])
                            device_key = str(result.get("ble_mac") or ip_addr)
                            # Deduplicate: keep only first response from each device identity
                            if device_key not in responses:
                                _LOGGER.info(
                                    "DISCOVERY: Found device at %s:%d - %s",
                                    ip_addr,
                                    addr[1],
                                    payload,
                                )
                                responses[device_key] = (ip_addr, addr[1], payload)
                            else:
                                _LOGGER.debug("Ignoring duplicate response from %s", device_key)
                        else:
                            _LOGGER.debug("Ignoring response without useful 'result' field from %s: %s", addr[0], payload)
                    except json.JSONDecodeError as je:
                        _LOGGER.debug("Non-JSON discovery response from %s: %s", addr, data[:100])
                    except Exception as e:
                        _LOGGER.debug("Error parsing discovery response from %s: %s", addr, e)
                        
                except socket.timeout:
                    # Normal - no response yet, continue broadcasting
                    continue
                except Exception as e:
                    _LOGGER.debug("Socket error during discovery: %s", e)
                    continue
            
            # Convert deduped dict back to list
            result = list(responses.values())
            _LOGGER.debug("Discovery finished after %.1f seconds, found %d unique device(s)", 
                         time.time() - start_time, len(result))
            return result
            
        except Exception as err:
            _LOGGER.exception("Discovery failed: %s", err)
            return []
        finally:
            try:
                sock.close()
            except Exception:
                pass

    @staticmethod
    def _get_discovery_targets(
        port: int,
        local_ips: set[str] | None = None,
    ) -> list[tuple[str, int]]:
        """Return UDP broadcast targets for discovery.

        The official API uses broadcast discovery, but some networks only forward
        interface-specific broadcasts. We try the global broadcast plus common
        subnet broadcasts derived from local IPv4 addresses.
        """

        targets: list[tuple[str, int]] = []
        seen: set[str] = set()

        def add_target(address: str) -> None:
            if address and address not in seen:
                targets.append((address, port))
                seen.add(address)

        add_target("255.255.255.255")

        if local_ips is None:
            local_ips = set(MarstekUDPClient._get_local_ipv4_addresses())

        for local_ip in local_ips:
            for prefix in (24, 16):
                try:
                    broadcast = str(ipaddress.ip_network(f"{local_ip}/{prefix}", strict=False).broadcast_address)
                except ValueError:
                    continue
                add_target(broadcast)

        return targets

    @staticmethod
    def _get_local_ipv4_addresses() -> list[str]:
        """Best-effort detection of local IPv4 addresses.

        This is intentionally conservative: we only use it to derive broadcast
        targets for discovery, and we ignore loopback or malformed addresses.
        """

        addresses: list[str] = []
        seen: set[str] = set()

        def add_address(address: str | None) -> None:
            if not address:
                return

            try:
                ip_obj = ipaddress.ip_address(address)
            except ValueError:
                return

            if ip_obj.version != 4 or ip_obj.is_loopback or ip_obj.is_link_local:
                return

            address_str = str(ip_obj)
            if address_str not in seen:
                addresses.append(address_str)
                seen.add(address_str)

        try:
            hostname = socket.gethostname()
            _host, _aliases, host_ips = socket.gethostbyname_ex(hostname)
            for ip in host_ips:
                add_address(ip)
        except Exception:
            pass

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe_sock:
                # This does not send packets; it only lets the OS pick a local route.
                probe_sock.connect(("1.1.1.1", 80))
                add_address(probe_sock.getsockname()[0])
        except Exception:
            pass

        return addresses


class _UDPClientProtocol(asyncio.DatagramProtocol):
    """UDP protocol handler for JSON-RPC responses."""

    def __init__(self, expected_id: int):
        """Initialize protocol.
        
        Args:
            expected_id: Expected request ID for this response
        """
        self.expected_id = expected_id
        self._response_future: asyncio.Future[dict] = asyncio.Future()

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Handle received UDP datagram.
        
        Args:
            data: Received data bytes
            addr: Source address tuple
        """
        try:
            response = json.loads(data.decode("utf-8"))
            
            # Marstek device always responds with id: 0, so accept it regardless of request ID
            # We still check for the expected ID first for compatibility, but fall back to id: 0
            if response.get("id") == self.expected_id or response.get("id") == 0:
                self._response_future.set_result(response)
            else:
                _LOGGER.warning("Received response with unexpected ID: %s (expected: %s)", 
                               response.get("id"), self.expected_id)
                
        except json.JSONDecodeError as err:
            self._response_future.set_exception(err)

    def error_received(self, exc: Exception) -> None:
        """Handle protocol error.
        
        Args:
            exc: Exception that occurred
        """
        self._response_future.set_exception(exc)

    async def get_response(self) -> dict[str, Any]:
        """Wait for and return the response.
        
        Returns:
            Response dictionary
        """
        return await self._response_future
