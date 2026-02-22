from odf.opendocument import load
from odf.table import Table, TableRow, TableCell
from odf.text import P
from io import BytesIO

def check_visa():
    """Check if SEARCH_NUMBER appears in the ODS file contents"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0 Safari/537.36",
            "Accept": "*/*"
        }
        response = requests.get(FILE_URL, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse the ODS file from memory
        ods_data = BytesIO(response.content)
        doc = load(ods_data)

        found = False
        for table in doc.getElementsByType(Table):
            for row in table.getElementsByType(TableRow):
                for cell in row.getElementsByType(TableCell):
                    text_content = "".join(t.data for t in cell.getElementsByType(P))
                    if SEARCH_NUMBER in text_content:
                        found = True
                        break
                if found:
                    break
            if found:
                break

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
