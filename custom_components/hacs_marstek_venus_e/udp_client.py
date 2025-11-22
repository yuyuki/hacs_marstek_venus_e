"""UDP JSON-RPC client for Marstek Venus E."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


class MarstekUDPClient:
    """UDP JSON-RPC client for communicating with Marstek Venus E device."""

    def __init__(self, ip_address: str, port: int = 30000, timeout: float = 10.0):
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
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id,
        }
        
        if params:
            payload["params"] = params
        
        try:
            # Create UDP socket
            loop = asyncio.get_event_loop()
            transport, protocol = await asyncio.wait_for(
                loop.create_datagram_endpoint(
                    lambda: _UDPClientProtocol(request_id),
                    remote_addr=(self.ip_address, self.port),
                ),
                timeout=self.timeout,
            )
            
            # Send request
            transport.sendto(json.dumps(payload).encode("utf-8"))
            
            # Wait for response
            response = await asyncio.wait_for(
                protocol.get_response(), timeout=self.timeout
            )
            
            # Clean up
            transport.close()
            
            # Parse and return response
            if "error" in response:
                raise Exception(f"RPC Error: {response['error']}")
            
            return response.get("result", {})
            
        except asyncio.TimeoutError:
            _LOGGER.error("Request timeout to %s:%s", self.ip_address, self.port)
            raise
        except Exception as err:
            _LOGGER.error("Error communicating with device: %s", err)
            raise

    async def get_realtime_data(self) -> dict[str, Any]:
        """Get real-time data from device.
        
        Returns:
            Dictionary containing real-time data
        """
        return await self._send_request("get_realtime_data")

    async def get_battery_info(self) -> dict[str, Any]:
        """Get battery information.
        
        Returns:
            Dictionary containing battery info
        """
        return await self._send_request("get_battery_info")

    async def set_mode(self, mode: str) -> dict[str, Any]:
        """Set operating mode.
        
        Args:
            mode: Mode name (Auto, AI, Manual, Passive)
            
        Returns:
            Response from device
        """
        return await self._send_request("set_mode", {"mode": mode})

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
            "set_manual_schedule",
            {
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
            "set_passive_mode",
            {"power": power, "cd_time": cd_time},
        )

    async def get_schedule(self) -> dict[str, Any]:
        """Get current schedule configuration.
        
        Returns:
            Current schedule data
        """
        return await self._send_request("get_schedule")


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
