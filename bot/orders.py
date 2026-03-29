
from __future__ import annotations

from typing import Any, Dict, Optional

from bot.client import BinanceFuturesClient, BinanceClientError, BinanceNetworkError
from bot.logging_config import setup_logger

logger = setup_logger("orders")


def _fmt_order_summary(params: Dict[str, Any]) -> str:
   
    parts = [
        f"Symbol : {params.get('symbol')}",
        f"Side   : {params.get('side')}",
        f"Type   : {params.get('type')}",
        f"Qty    : {params.get('quantity')}",
    ]
    if "price" in params:
        parts.append(f"Price  : {params['price']}")
    if "stopPrice" in params:
        parts.append(f"StopPx : {params['stopPrice']}")
    return "\n  ".join(parts)


def _fmt_order_response(resp: Dict[str, Any]) -> str:
    lines = [
        f"Order ID    : {resp.get('orderId')}",
        f"Client OID  : {resp.get('clientOrderId')}",
        f"Symbol      : {resp.get('symbol')}",
        f"Status      : {resp.get('status')}",
        f"Side        : {resp.get('side')}",
        f"Type        : {resp.get('type')}",
        f"Orig Qty    : {resp.get('origQty')}",
        f"Exec Qty    : {resp.get('executedQty')}",
        f"Avg Price   : {resp.get('avgPrice', 'N/A')}",
        f"Price       : {resp.get('price', 'N/A')}",
        f"Time        : {resp.get('updateTime')}",
    ]
    return "\n  ".join(lines)


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
) -> Dict[str, Any]:
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }

    logger.info("Placing MARKET order:")
    logger.info(f"  {_fmt_order_summary(params)}")

    response = client.place_order(**params)

    logger.info("MARKET order placed successfully:")
    logger.info(f"  {_fmt_order_response(response)}")
    return response


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
  
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": time_in_force,
    }

    logger.info("Placing LIMIT order:")
    logger.info(f"  {_fmt_order_summary(params)}")

    response = client.place_order(**params)

    logger.info("LIMIT order placed successfully:")
    logger.info(f"  {_fmt_order_response(response)}")
    return response


def place_stop_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
) -> Dict[str, Any]:
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP_MARKET",
        "quantity": quantity,
        "stopPrice": stop_price,
    }

    logger.info("Placing STOP_MARKET order:")
    logger.info(f"  {_fmt_order_summary(params)}")

    response = client.place_order(**params)

    logger.info("STOP_MARKET order placed successfully:")
    logger.info(f"  {_fmt_order_response(response)}")
    return response


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    if order_type == "MARKET":
        return place_market_order(client, symbol, side, quantity)

    elif order_type == "LIMIT":
        if price is None:
            raise ValueError("price is required for LIMIT orders.")
        return place_limit_order(client, symbol, side, quantity, price)

    elif order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValueError("stop_price is required for STOP_MARKET orders.")
        return place_stop_market_order(client, symbol, side, quantity, stop_price)

    else:
        raise ValueError(f"Unsupported order type: {order_type}")
