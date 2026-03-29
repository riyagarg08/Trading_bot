
from __future__ import annotations

import re
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}

SYMBOL_PATTERN = re.compile(r"^[A-Z]{2,10}(USDT|BUSD|BTC|ETH|BNB)$")

class ValidationError(ValueError):
   


def validate_symbol(symbol: str) -> str:
  
    symbol = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(symbol):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. "
            "Expected format: <BASE><QUOTE>, e.g. BTCUSDT, ETHUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return side


def validate_order_type(order_type: str) -> str:
   
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
  
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")

    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0. Got: {qty}.")
    return qty


def validate_price(price: Optional[str | float]) -> Optional[float]:
   
    if price is None:
        return None

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")

    if p <= 0:
        raise ValidationError(f"Price must be greater than 0. Got: {p}.")
    return p


def validate_stop_price(stop_price: Optional[str | float]) -> Optional[float]:
   
    return validate_price(stop_price)  # Same rules as price


# ── Composite validator ─────────────────────────────────────────────────────────
def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: Optional[str | float] = None,
    stop_price: Optional[str | float] = None,
) -> dict:
   
    clean = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    if clean["order_type"] == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        clean["price"] = validate_price(price)

    elif clean["order_type"] == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("--stop-price is required for STOP_MARKET orders.")
        clean["stop_price"] = validate_stop_price(stop_price)
        if price is not None:
            clean["price"] = validate_price(price)

    elif clean["order_type"] == "MARKET" and price is not None:
        raise ValidationError("Price should not be provided for MARKET orders.")

    return clean
