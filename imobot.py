import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

TABLE_URL = "https://www.imoova.com/en/relocations/table?region=EU"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

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
        # Depending on column order: adjust indexes accordingly
        from_city = cols[1]
        to_city = cols[2]
        depart = cols[3]
        price = cols[5]
        deals.append({
            "from": from_city,
            "to": to_city,
            "depart": depart,
            "price": price,
            "raw": " | ".join(cols)
        })
    return deals

def main():
    deals = fetch_deals_table()
    bcn = [d for d in deals if d["from"].lower() == "barcelona" or d["to"].lower() == "barcelona"]
    if bcn:
        send_telegram("🚐 Imoova — Barcelona-related relocation(s) found!")
        for d in bcn:
            send_telegram(f'{d["from"]} → {d["to"]} — {d["depart"]} — {d["price"]}')
    else:
        print("No Barcelona deals found.")

if __name__ == "__main__":
    main()

