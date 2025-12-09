import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.imoova.com/en/relocations?region=EU"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def get_relocations():
    r = requests.get(URL, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    deals = []
    selectors = [".imoova-card", ".vehicle-card", ".deal-card", ".card"]

    for sel in selectors:
        for card in soup.select(sel):
            deals.append(card.get_text(" ", strip=True).lower())

    return deals


def find_barcelona_deals(deals):
    return [d for d in deals if "barcelona" in d]


def main():
    try:
        deals = get_relocations()
        bcn_deals = find_barcelona_deals(deals)

        if bcn_deals:
            send_telegram("🔥 Barcelona deals found:")
            for d in bcn_deals:
                send_telegram(d)
        else:
            print("No Barcelona deals now.")

    except Exception as e:
        send_telegram(f"⚠️ Error in bot: {e}")
        raise e


if __name__ == "__main__":
    main()

