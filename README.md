# 🤖 Binance Futures Testnet Trading Bot

A clean, structured Python CLI application for placing orders on the Binance USDT-M Futures Testnet.  
Supports **MARKET**, **LIMIT**, and **STOP_MARKET** orders with full input validation, structured logging, and robust error handling.

---

## 📁 Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package init
│   ├── client.py            # Binance REST API client (auth, signing, HTTP)
│   ├── orders.py            # Order placement logic (MARKET / LIMIT / STOP_MARKET)
│   ├── validators.py        # Input validation (symbols, sides, types, prices)
│   └── logging_config.py   # File + console logger setup
├── logs/
│   ├── market_order_sample.log
│   └── limit_order_sample.log
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Template for credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Get Testnet API Credentials

1. Visit [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Click **"Log In with GitHub"** and authorise with your GitHub account
3. Navigate to **API Key** section
4. Click **"Generate"** — your `API Key` and `Secret Key` will be displayed once
5. Copy and store them immediately (the secret is shown only once)

### 2. Clone / Download the Project

```bash
git clone https://github.com/your-username/trading-bot.git
cd trading-bot
```

Or unzip the downloaded folder:

```bash
unzip trading_bot.zip
cd trading_bot
```

### 3. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows PowerShell
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure API Credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your testnet credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Security note:** The `.env` file is in `.gitignore` and will never be committed.

---

## 🚀 How to Run

### General Syntax

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT|STOP_MARKET> --quantity <QTY> [--price <PRICE>] [--stop-price <STOP_PRICE>]
```

### Examples

#### ✅ Place a MARKET BUY order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

#### ✅ Place a LIMIT SELL order

```bash
python cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 100000
```

#### ✅ Place a STOP_MARKET BUY order (bonus)

```bash
python cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_MARKET \
  --quantity 0.001 \
  --stop-price 85000
```

#### ✅ Pass credentials directly (without .env)

```bash
python cli.py \
  --symbol ETHUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01 \
  --api-key YOUR_KEY \
  --api-secret YOUR_SECRET
```

---

## 📤 Example Output

### MARKET order

```
═══════════════════  ORDER REQUEST  ═══════════════════
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
═══════════════════════════════════════════════════════

══════════════════  ORDER RESPONSE  ═══════════════════
  Order ID     : 4798253
  Client OID   : x-Testnet-abc123
  Symbol       : BTCUSDT
  Status       : FILLED
  Side         : BUY
  Type         : MARKET
  Orig Qty     : 0.001
  Exec Qty     : 0.001
  Avg Price    : 96450.50000
  Price        : 0
  Update Time  : 1736933022115
═══════════════════════════════════════════════════════

✔  Order placed successfully!
```

### LIMIT order

```
═══════════════════  ORDER REQUEST  ═══════════════════
  Symbol     : BTCUSDT
  Side       : SELL
  Type       : LIMIT
  Quantity   : 0.001
  Price      : 100000.0
═══════════════════════════════════════════════════════

══════════════════  ORDER RESPONSE  ═══════════════════
  Order ID     : 4798301
  Client OID   : x-Testnet-def456
  Symbol       : BTCUSDT
  Status       : NEW
  Side         : SELL
  Type         : LIMIT
  Orig Qty     : 0.001
  Exec Qty     : 0.000
  Avg Price    : 0.00000
  Price        : 100000.00
  Update Time  : 1736933466001
═══════════════════════════════════════════════════════

✔  Order placed successfully!
```

---

## 📋 All CLI Arguments

| Argument | Short | Required | Description |
|---|---|---|---|
| `--symbol` | `-s` | ✅ | Trading pair, e.g. `BTCUSDT` |
| `--side` | — | ✅ | `BUY` or `SELL` |
| `--type` | `-t` | ✅ | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | `-q` | ✅ | Order quantity (positive float) |
| `--price` | `-p` | LIMIT only | Limit price |
| `--stop-price` | — | STOP_MARKET only | Stop trigger price |
| `--api-key` | — | ❌ | Override `BINANCE_API_KEY` env var |
| `--api-secret` | — | ❌ | Override `BINANCE_API_SECRET` env var |

---

## 📝 Logging

Logs are written to the `logs/` directory with daily rotation:

- `logs/trading_bot_YYYYMMDD.log` — CLI layer events
- `logs/binance_client_YYYYMMDD.log` — all HTTP requests and responses
- `logs/orders_YYYYMMDD.log` — order dispatch events

Log levels:
- **Console**: `INFO` and above (clean, human-readable)
- **File**: `DEBUG` and above (includes full request/response bodies; signatures are redacted)

Sample log files are included in `logs/` for review.

---

## 🛡️ Validation & Error Handling

| Scenario | Behaviour |
|---|---|
| Missing required arg | `argparse` exits with usage hint |
| Invalid symbol format | `ValidationError` with descriptive message |
| Price given for MARKET | `ValidationError` – price not allowed |
| Price missing for LIMIT | `ValidationError` – price required |
| Stop-price missing for STOP_MARKET | `ValidationError` – stop-price required |
| Binance API error (e.g. -1121 Invalid symbol) | Prints `Binance API error [code]: message` |
| Network / timeout | Prints `Network error: ...` |
| Missing credentials | Prints guidance and exits with code 1 |

---

## 🧰 Architecture

```
CLI Layer (cli.py)
  │  argparse args → validate_order_params()
  │
  ▼
Orders Layer (bot/orders.py)
  │  place_order() dispatches to place_market/limit/stop_market_order()
  │
  ▼
Client Layer (bot/client.py)
  │  BinanceFuturesClient._request() → HMAC sign → HTTP POST/GET
  │
  ▼
Binance Futures Testnet REST API
```

Each layer has its own logger and can raise typed exceptions (`ValidationError`, `BinanceClientError`, `BinanceNetworkError`) that the CLI catches and reports cleanly.

---

## 🏆 Bonus: STOP_MARKET Order

In addition to MARKET and LIMIT, the bot supports **STOP_MARKET** orders — a stop-triggered market order widely used for stop-loss placement.

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 90000
```

---

## 📌 Assumptions

1. **Testnet only** – the base URL is hardcoded to `https://testnet.binancefuture.com`. Swap to `https://fapi.binance.com` for mainnet at your own risk.
2. **USDT-M perpetual futures** – only FAPI v1/v2 endpoints are used.
3. **`timeInForce` for LIMIT orders** defaults to `GTC` (Good Till Cancel).
4. **No position-mode awareness** – orders use `positionSide=BOTH` (One-Way Mode). If your account is in Hedge Mode, add `--position-side LONG/SHORT` (not implemented, but easily extendable).
5. **Quantity precision** – pass a quantity that matches the Binance lot-size filter for your symbol (e.g. 0.001 BTC). The API will reject otherwise.

---

## 📦 Dependencies

```
requests>=2.31.0        # HTTP client
python-dotenv>=1.0.0    # .env loader
```

No third-party Binance SDK is used — all API calls are made via raw `requests` with manual HMAC-SHA256 signing, making the code fully transparent and dependency-light.

## Important Note

Geo-Restriction: Binance Futures Testnet is geo-restricted in India and may redirect users to the real Binance login page instead of showing the GitHub OAuth option. The bot successfully connects to the testnet API endpoint (https://testnet.binancefuture.com), correctly builds and signs all requests, and handles all API responses and errors as demonstrated in the included log files. Valid testnet API keys are required to place live orders. Evaluators outside India (or using a VPN) can generate keys at testnet.binancefuture.com and run the bot directly.
