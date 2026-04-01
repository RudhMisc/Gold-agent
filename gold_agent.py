import os
import time
import requests
from datetime import datetime

# ─────────────────────────────────────────────

# CONFIGURATION  ← only edit this section

# ─────────────────────────────────────────────

TELEGRAM_TOKEN = os.environ.get(“TELEGRAM_TOKEN”, “”)   # your bot token
TELEGRAM_CHAT_ID = os.environ.get(“TELEGRAM_CHAT_ID”, “”) # your chat ID
GOLDAPI_KEY = os.environ.get(“GOLDAPI_KEY”, “”)           # your GoldAPI key
CHECK_INTERVAL = 300   # check every 5 minutes (seconds)

# ─────────────────────────────────────────────

CURRENCIES = {
“Chennai (INR)”: “INR”,
“Dubai  (AED)”: “AED”,
}

last_prices = {}

def fetch_gold_price(currency: str) -> float | None:
“”“Fetch gold price per gram in the given currency via GoldAPI.”””
url = f”https://www.goldapi.io/api/XAU/{currency}”
headers = {“x-access-token”: GOLDAPI_KEY}
try:
r = requests.get(url, headers=headers, timeout=10)
r.raise_for_status()
data = r.json()
price_per_oz = data.get(“price”)
if price_per_oz:
return round(price_per_oz / 31.1035, 2)   # convert oz → gram
except Exception as e:
print(f”[{datetime.now()}] Error fetching {currency}: {e}”)
return None

def send_telegram(message: str):
“”“Send a Telegram message.”””
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
print(“Telegram not configured — skipping notification.”)
return
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {“chat_id”: TELEGRAM_CHAT_ID, “text”: message, “parse_mode”: “Markdown”}
try:
requests.post(url, json=payload, timeout=10)
except Exception as e:
print(f”[{datetime.now()}] Telegram error: {e}”)

def format_change(old: float, new: float) -> str:
diff = new - old
pct = (diff / old) * 100
arrow = “📈” if diff > 0 else “📉”
return f”{arrow} {’+’ if diff > 0 else ‘’}{diff:.2f} ({pct:+.2f}%)”

def check_prices():
global last_prices
now = datetime.now().strftime(”%d %b %Y, %H:%M”)
alerts = []

```
for label, currency in CURRENCIES.items():
    price = fetch_gold_price(currency)
    if price is None:
        continue

    symbol = "₹" if currency == "INR" else "AED"
    prev = last_prices.get(currency)

    if prev is None:
        # First run — just store and notify startup
        last_prices[currency] = price
        alerts.append(f"*{label}*\n{symbol}{price:,.2f}/gram\n_(baseline set)_")
    elif price != prev:
        change_str = format_change(prev, price)
        last_prices[currency] = price
        alerts.append(f"*{label}*\n{symbol}{price:,.2f}/gram\n{change_str}")

if alerts:
    header = f"🥇 *Gold Price Update* — {now}\n{'─'*30}"
    message = header + "\n\n" + "\n\n".join(alerts)
    print(message.replace("*", "").replace("_", ""))
    send_telegram(message)
else:
    print(f"[{datetime.now()}] No price change detected.")
```

def main():
print(”=” * 45)
print(”  Gold Price Monitor — Chennai & Dubai”)
print(”=” * 45)
if not GOLDAPI_KEY:
print(“ERROR: GOLDAPI_KEY not set. See setup guide.”)
return
print(f”Checking every {CHECK_INTERVAL // 60} minutes. Press Ctrl+C to stop.\n”)
send_telegram(“✅ *Gold Monitor started!*\nWatching Chennai (INR) & Dubai (AED)…”)
while True:
check_prices()
time.sleep(CHECK_INTERVAL)

if **name** == “**main**”:
main()
