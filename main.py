import requests
from datetime import datetime
from flask import Flask, request
import os
import time
from io import BytesIO
from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P

# --- CONFIG ---
FILE_URL = "https://www.ireland.ie/4468/20260219_NDVO_Visa_Decisions.ods"
SEARCH_NUMBER = "72571452"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
# ---------------

app = Flask(__name__)

# Prevent spam if checked frequently
last_check_time = 0
MIN_INTERVAL = 3600  # seconds (1 hour)


def send_telegram(message):
    """Send message to Telegram chat"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ Telegram send failed: {e}")


def check_visa():
    """Fetch and check the visa number inside the ODS file"""
    global last_check_time

    # Rate limit (only once per hour)
    if time.time() - last_check_time < MIN_INTERVAL:
        return f"⏱ Skipped duplicate run at {datetime.now()}"

    last_check_time = time.time()

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            ),
            "Accept": "*/*"
        }
        response = requests.get(FILE_URL, headers=headers, timeout=30)
        response.raise_for_status()

        ods_data = BytesIO(response.content)
        doc = load(ods_data)

        found = False
        for table in doc.getElementsByType(Table):
            for row in table.getElementsByType(TableRow):
                for cell in row.getElementsByType(TableCell):
                    text_content = "".join(str(p) for p in cell.getElementsByType(P))
                    if SEARCH_NUMBER in text_content:
                        found = True
                        break
                if found:
                    break
            if found:
                break

        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if found:
            msg = f"✅ Visa number {SEARCH_NUMBER} FOUND at {time_str}."
        else:
            msg = f"❌ Visa number {SEARCH_NUMBER} NOT found at {time_str}."

        send_telegram(msg)
        return msg

    except Exception as e:
        err = f"⚠️ Error checking visa status: {e}"
        send_telegram(err)
        return err


@app.route("/", methods=["GET", "HEAD"])
def home():
    """Endpoint for browser and UptimeRobot"""
    result = check_visa()
    if request.method == "HEAD":
        # Return lightweight response for UptimeRobot
        return ("OK", 200)
    return f"<h3>{result}</h3>"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
