import requests
from bs4 import BeautifulSoup
import time

# ------------------------------
#  TELEGRAM CONFIG
# ------------------------------
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ------------------------------
#  SCRAPER FUNCTIONS
# ------------------------------
URL = "https://www.imoova.com/en/relocations?region=EU"

def get_relocations():
    r = requests.get(URL, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    deals = []
    # Try multiple potential card classes (IMOOVA changes HTML sometimes)
    selectors = [".imoova-card", ".vehicle-card", ".deal-card", ".card"]

    for sel in selectors:
        for card in soup.select(sel):
            text = card.get_text(" ", strip=True)
            deals.append(text.lower())

    return deals

def find_barcelona_deals(deals):
    return [d for d in deals if "barcelona" in d]


# ------------------------------
#  MAIN LOOP
# ------------------------------
if __name__ == "__main__":
    send_telegram("🤖 IMOOVA Barcelona bot started.")
    last_seen = set()

    while True:
        try:
            deals = get_relocations()
            bcn_deals = find_barcelona_deals(deals)

            new = set(bcn_deals) - last_seen

            if new:
                for d in new:
                    send_telegram("🔥 NEW Barcelona deal found:\n" + d)
                last_seen = set(bcn_deals)

        except Exception as e:
            send_telegram(f"⚠️ Error occurred: {e}")

        time.sleep(1800)   # check every 30 minutes

