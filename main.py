import requests
from datetime import datetime
import os

FILE_URL = "https://www.ireland.ie/4468/20260219_NDVO_Visa_Decisions.ods"
SEARCH_NUMBER = "81861692"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def check_visa():
    """Check if SEARCH_NUMBER appears in the ODS file text"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0 Safari/537.36",
            "Accept": "*/*"
        }
        response = requests.get(FILE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        content = response.content.decode("latin1", errors="ignore")

        found = SEARCH_NUMBER in content
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if found:
            send_telegram(f"✅ Visa number {SEARCH_NUMBER} FOUND at {time}.")
        else:
            send_telegram(f"❌ Visa number {SEARCH_NUMBER} NOT found at {time}.")
    except Exception as e:
        send_telegram(f"⚠️ Error checking visa status: {e}")

if __name__ == "__main__":
    check_visa()
