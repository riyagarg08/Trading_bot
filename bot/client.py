

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_RECV_WINDOW = 5000  # ms


class BinanceClientError(Exception):
   

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceNetworkError(Exception):
class BinanceFuturesClient:
   

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        recv_window: int = DEFAULT_RECV_WINDOW,
    ):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.recv_window = recv_window
        self.logger = setup_logger("binance_client")

        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        self.logger.info(f"BinanceFuturesClient initialised. Base URL: {self.base_url}")


    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = self._timestamp()
        params["recvWindow"] = self.recv_window
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = True,
    ) -> Dict[str, Any]:
       
        params = params or {}
        url = f"{self.base_url}{endpoint}"

        if signed:
            params = self._sign(params)

        self.logger.debug(
            f"REQUEST  {method} {endpoint} | params={self._redact(params)}"
        )

        try:
            if method == "GET":
                response = self._session.get(url, params=params, timeout=10)
            elif method == "POST":
                response = self._session.post(url, data=params, timeout=10)
            elif method == "DELETE":
                response = self._session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.ConnectionError as exc:
            self.logger.error(f"Network error – {exc}")
            raise BinanceNetworkError(f"Connection failed: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            self.logger.error(f"Request timed out – {exc}")
            raise BinanceNetworkError(f"Request timed out: {exc}") from exc

        self.logger.debug(
            f"RESPONSE {method} {endpoint} | status={response.status_code} | body={response.text[:500]}"
        )

        data = response.json()
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            code = data["code"]
            msg = data.get("msg", "Unknown error")
            self.logger.error(f"Binance API error | code={code} | msg={msg}")
            raise BinanceClientError(code, msg)

        return data

    @staticmethod
    def _redact(params: Dict[str, Any]) -> Dict[str, Any]:
        redacted = dict(params)
        if "signature" in redacted:
            redacted["signature"] = "***"
        return redacted


    def get_account(self) -> Dict[str, Any]:
     
        return self._request("GET", "/fapi/v2/account")

    def place_order(self, **kwargs) -> Dict[str, Any]:
        
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def query_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        
        return self._request(
            "GET",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
        )

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
       
        return self._request(
            "DELETE",
            "/fapi/v1/order",
            params={"symbol": symbol, "orderId": order_id},
        )
