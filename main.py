import requests
from datetime import datetime
from flask import Flask
import os

FILE_URL = "https://www.ireland.ie/4468/20260219_NDVO_Visa_Decisions.ods"
SEARCH_NUMBER = "72571452"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

app = Flask(__name__)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def check_visa():
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
            msg = f"✅ Visa number {SEARCH_NUMBER} FOUND at {time}."
        else:
            msg = f"❌ Visa number {SEARCH_NUMBER} NOT found at {time}."
        send_telegram(msg)
        return msg
    except Exception as e:
        err = f"⚠️ Error checking visa status: {e}"
        send_telegram(err)
        return err

@app.route("/")
def home():
    result = check_visa()
    return f"<h3>{result}</h3>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
