import requests
from bs4 import BeautifulSoup
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ.get("CHAT_ID")  # optional default chat
TABLE_URL = "https://www.imoova.com/en/relocations/table?region=EU"

# ------------------------------
# Telegram helpers
# ------------------------------
def send_telegram(msg, chat_id=None):
    chat_id = chat_id or CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 60}
    if offset:
        params["offset"] = offset
    resp = requests.get(url, params=params)
    return resp.json().get("result", [])

# ------------------------------
# Scraper
# ------------------------------
def fetch_deals_table():
    r = requests.get(TABLE_URL, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if table is None:
        return []

    rows = table.find_all("tr")[1:]  # skip header
    deals = []
    for tr in rows:
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) < 6:
            continue
        deals.append({
            "from": cols[1].lower(),
            "to": cols[2].lower(),
            "depart": cols[3],
            "price": cols[5],
            "raw": " | ".join(cols)
        })
    return deals

def find_city_deals(city, deals):
    city = city.lower()
    return [d for d in deals if city in (d["from"], d["to"])]

# ------------------------------
# Main loop
# ------------------------------
def main():
    print("🤖 IMOOVA City Bot started.")
    offset = None
    deals = fetch_deals_table()

    while True:
        updates = get_updates(offset)
        for u in updates:
            offset = u["update_id"] + 1
            if "message" in u and "text" in u["message"]:
                chat_id = u["message"]["chat"]["id"]
                city = u["message"]["text"].strip()
                matched = find_city_deals(city, deals)
                if matched:
                    send_telegram(f"🚐 Relocations related to {city}:", chat_id)
                    for d in matched:
                        send_telegram(f'{d["from"]} → {d["to"]} — {d["depart"]} — {d["price"]}', chat_id)
                else:
                    send_telegram(f"No relocations found for {city}.", chat_id)

if __name__ == "__main__":
    main()

