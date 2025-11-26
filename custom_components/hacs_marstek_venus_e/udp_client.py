"""UDP JSON-RPC client for Marstek Venus E."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class MarstekUDPClient:
    """UDP JSON-RPC client for communicating with Marstek Venus E device."""

    def __init__(self, ip_address: str, port: int = 30000, timeout: float = 5.0):
        """Initialize the UDP client.
        
        Args:
            ip_address: IP address of the device
            port: UDP port (default 30000)
            timeout: Request timeout in seconds
        """
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self._request_id = 0

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

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
                _LOGGER.debug("Sent %s request to %s:%d", method, self.ip_address, self.port)
                
                response = await asyncio.wait_for(
                    protocol.get_response(), timeout=self.timeout
                )
                
                transport.close()
                
                if "error" in response:
                    error = response.get("error", {})
                    error_msg = f"{error.get('message', 'Unknown error')} (code: {error.get('code')})"
                    _LOGGER.error("RPC Error from %s:%d: %s", self.ip_address, self.port, error_msg)
                    raise Exception(f"RPC Error: {error_msg}")
                
                result = response.get("result", {})
                _LOGGER.debug("Received response from %s:%d: %s", self.ip_address, self.port, result)
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
        """Get operating mode.
        
        Returns:
            Dictionary containing mode information
        """
        return await self._send_request("ES.GetMode", {"id": 0})

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

    async def set_mode(self, mode: str) -> dict[str, Any]:
        """Set operating mode.
        
        Args:
            mode: Mode name (Auto, AI, Manual, Passive)
            
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
            config["manual_cfg"] = {"enable": 1}
        elif mode == "Passive":
            config["passive_cfg"] = {"enable": 1}
        
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
        
        Args:
            time_num: Time slot number (1-4)
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            week_set: Week bitmask (1=Mon, 2=Tue, ..., 64=Sun, 127=All)
            power: Power in watts (negative=charge, positive=discharge)
            enable: Enable the schedule
            
        Returns:
            Response from device
        """
        return await self._send_request(
            "ES.SetSchedule",
            {
                "id": 0,
                "time_num": time_num,
                "start_time": start_time,
                "end_time": end_time,
                "week_set": week_set,
                "power": power,
                "enable": enable,
            },
        )

    async def set_passive_mode(self, power: int, cd_time: int = 0) -> dict[str, Any]:
        """Set passive mode with power target.
        
        Args:
            power: Target power in watts
            cd_time: Countdown time in seconds (0 = indefinite)
            
        Returns:
            Response from device
        """
        return await self._send_request(
            "ES.SetPassiveMode",
            {"id": 0, "power": power, "cd_time": cd_time},
        )

    @staticmethod
    async def discover(timeout: float = 15.0, port: int = 30000) -> list[tuple[str, int, dict[str, Any]]]:
        """Discover Marstek devices on the local network via UDP broadcast.

        Sends a JSON-RPC discovery probe as a UDP broadcast and collects
        any JSON responses received within `timeout` seconds.

        Returns a list of tuples: (ip, port, parsed_json_response).
        Deduplicates responses by IP address and filters out invalid responses.
        """
        import socket
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
        
        # Create socket bound to the discovery port (important!)
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
        
        responses: dict[str, tuple[str, int, dict[str, Any]]] = {}  # Use dict to deduplicate by IP
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
                        sock.sendto(probe_bytes, ("255.255.255.255", port))
                        _LOGGER.debug("Sent discovery probe to 255.255.255.255:%d", port)
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
                        if "result" in payload:
                            ip_addr = addr[0]
                            # Deduplicate: keep only first response from each IP
                            if ip_addr not in responses:
                                _LOGGER.info("DISCOVERY: Found device at %s:%d - %s", addr[0], addr[1], payload)
                                responses[ip_addr] = (addr[0], addr[1], payload)
                            else:
                                _LOGGER.debug("Ignoring duplicate response from %s", ip_addr)
                        else:
                            _LOGGER.debug("Ignoring response without 'result' field from %s: %s", addr[0], payload)
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
            
            # Verify response ID matches request
            if response.get("id") == self.expected_id:
                self._response_future.set_result(response)
            else:
                _LOGGER.warning("Received response with mismatched ID")
                
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
