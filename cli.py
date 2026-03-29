#!/usr/bin/env python3


from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceClientError, BinanceNetworkError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import validate_order_params, ValidationError

# Load .env if present
load_dotenv()

logger = setup_logger("cli")
GREEN = "\033[92m"
RED   = "\033[91m"
CYAN  = "\033[96m"
BOLD  = "\033[1m"
RESET = "\033[0m"

def _c(text: str, colour: str) -> str:
    """Wrap text in ANSI colour codes (only when stdout is a TTY)."""
    if sys.stdout.isatty():
        return f"{colour}{text}{RESET}"
    return text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description=(
            "Binance Futures Testnet – order placement CLI\n"
            "Supports: MARKET, LIMIT, STOP_MARKET orders on USDT-M futures."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET     --quantity 0.001
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT       --quantity 0.01  --price 3500
  python cli.py --symbol BTCUSDT --side BUY  --type STOP_MARKET --quantity 0.001 --stop-price 85000
        """,
    )

    parser.add_argument(
        "--symbol", "-s",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type", "-t",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        type=str.upper,
        help="Order type: MARKET, LIMIT, or STOP_MARKET",
    )
    parser.add_argument(
        "--quantity", "-q",
        required=True,
        type=float,
        help="Order quantity (number of contracts)",
    )
    parser.add_argument(
        "--price", "-p",
        type=float,
        default=None,
        help="Limit price (required for LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price",
        type=float,
        default=None,
        dest="stop_price",
        help="Stop trigger price (required for STOP_MARKET orders)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Binance API key (overrides BINANCE_API_KEY env var)",
    )
    parser.add_argument(
        "--api-secret",
        default=None,
        help="Binance API secret (overrides BINANCE_API_SECRET env var)",
    )
    return parser

def print_request_summary(params: dict) -> None:
    print()
    print(_c("═══════════════════  ORDER REQUEST  ═══════════════════", CYAN))
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {_c(params['side'], GREEN if params['side'] == 'BUY' else RED)}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if "price" in params:
        print(f"  Price      : {params['price']}")
    if "stop_price" in params:
        print(f"  Stop Price : {params['stop_price']}")
    print(_c("═", CYAN))
    print()


def print_order_response(resp: dict) -> None:
    status = resp.get("status", "UNKNOWN")
    colour = GREEN if status in ("FILLED", "NEW") else RED

    print()
    print(_c(" ORDER RESPONSE ", CYAN))
    print(f"  Order ID     : {resp.get('orderId')}")
    print(f"  Client OID   : {resp.get('clientOrderId')}")
    print(f"  Symbol       : {resp.get('symbol')}")
    print(f"  Status       : {_c(status, colour)}")
    print(f"  Side         : {resp.get('side')}")
    print(f"  Type         : {resp.get('type')}")
    print(f"  Orig Qty     : {resp.get('origQty')}")
    print(f"  Exec Qty     : {resp.get('executedQty')}")
    print(f"  Avg Price    : {resp.get('avgPrice', 'N/A')}")
    print(f"  Price        : {resp.get('price', 'N/A')}")
    print(f"  Update Time  : {resp.get('updateTime')}")
    print(_c("═", CYAN))
    print()

def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    api_key    = args.api_key    or os.getenv("BINANCE_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        print(
            _c(
                "ERROR: API credentials not found.\n"
                "Set BINANCE_API_KEY and BINANCE_API_SECRET in your environment or .env file,\n"
                "or pass --api-key / --api-secret as CLI arguments.",
                RED,
            )
        )
        logger.error("Missing API credentials. Aborting.")
        return 1
    try:
        clean_params = validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        print(_c(f"Validation error: {exc}", RED))
        logger.error(f"Validation failed: {exc}")
        return 1

    print_request_summary(clean_params)
    logger.info(
        f"Validated order params: symbol={clean_params['symbol']} "
        f"side={clean_params['side']} type={clean_params['order_type']} "
        f"qty={clean_params['quantity']}"
    )

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        print(_c(f"Client init error: {exc}", RED))
        logger.error(f"Client init failed: {exc}")
        return 1

    try:
        response = place_order(
            client=client,
            symbol=clean_params["symbol"],
            side=clean_params["side"],
            order_type=clean_params["order_type"],
            quantity=clean_params["quantity"],
            price=clean_params.get("price"),
            stop_price=clean_params.get("stop_price"),
        )
    except ValidationError as exc:
        print(_c(f"Order error: {exc}", RED))
        logger.error(f"Order placement validation error: {exc}")
        return 1
    except BinanceClientError as exc:
        print(_c(f"Binance API error [{exc.code}]: {exc.message}", RED))
        logger.error(f"Binance API error: {exc}")
        return 1
    except BinanceNetworkError as exc:
        print(_c(f"Network error: {exc}", RED))
        logger.error(f"Network error: {exc}")
        return 1
    except Exception as exc:
        print(_c(f"Unexpected error: {exc}", RED))
        logger.exception(f"Unexpected error during order placement: {exc}")
        return 1

    print_order_response(response)
    print(_c("✔  Order placed successfully!", GREEN + BOLD))
    logger.info(
        f"Order placed successfully. orderId={response.get('orderId')} "
        f"status={response.get('status')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
