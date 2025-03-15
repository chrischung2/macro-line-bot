import mysql.connector
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from credentials import DB_CONFIG, LINE_ACCESS_TOKEN, USER_ID  # Import credentials
import time

# Helper function to log messages with a timestamp
def log(message):
    print(f"[{datetime.now()}] {message}")

# ✅ Function to Check for Updates in the Last 24 Hours
def check_new_updates():
    try:
        # Connect to MySQL Database
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(buffered=True)

        # Get the Timestamp for 24 Hours Ago
        yesterday = datetime.now() - timedelta(days=1)

        # Fetch Updated Indicators and Their Latest & Previous Values
        query = """
            SELECT i.indicator_name, i.abbreviation, d.value AS latest_value, 
                   (SELECT d2.value FROM indicator_data d2 
                    WHERE d2.indicator_id = d.indicator_id 
                    AND d2.record_date < d.record_date 
                    ORDER BY d2.record_date DESC LIMIT 1) AS previous_value
            FROM indicator_data d
            JOIN indicators i ON d.indicator_id = i.indicator_id
            WHERE d.last_updated >= %s
            ORDER BY d.last_updated DESC
            LIMIT 100;
        """

        start_time = time.time()
        cursor.execute(query, (yesterday,))
        updated_data = cursor.fetchall()
        elapsed = time.time() - start_time
        log(f"DEBUG: Query executed in {elapsed:.2f} seconds.")

        if updated_data:
            log(f"✅ {len(updated_data)} new data points found! Sending notification...")
            return updated_data
        else:
            log("✅ No new data found in the last 24 hours.")
            return []

    except mysql.connector.Error as err:
        log(f"❌ Database Error: {err}")
        return []
    except KeyboardInterrupt:
        log("Query interrupted by user.")
        return []

    finally:
        if 'cursor' in locals() and cursor is not None:
            try:
                cursor.close()
            except Exception as e:
                log(f"Error closing cursor: {e}")
        if 'db' in locals() and db.is_connected():
            db.close()

# ----------------------------------------------------------------------------
# Helper function for formatting values based on the indicator abbreviation.
def format_value(abbrev, value):
    """
    Format the given value based on the indicator abbreviation.
    
    The formatting rules mimic the following query_templates:
      - For yoy_growth and percentage: round to 2 decimals and add '%'
      - For monetary: prepend '$' and round to 2 decimals
      - For large_numbers: format with commas and no decimals
      - For hours: round to 1 decimal and append ' hrs'
      - For decimal_2: round to 2 decimals
      - For no_decimals: multiply by 1000 and format with no decimals
      - For billions: divide by 1000, round to 2 decimals, prepend '$', and append ' B'
    
    Adjust the rules below as needed.
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    # Define the formatting categories
    format_types = {
        "yoy_growth": ["CPI", "HPI", "PPI", "PCE"],
        "percentage": ["GDP", "FFR", "MORTG", "UR", "LFPR", "V", "10YY", "YCURV", "BSPRD"],
        "monetary": ["WAGE"],
        "large_numbers": ["NFP", "RTSAL", "XHOME", "TBLNC", "M2"],
        "hours": ["AWH"],
        "decimal_2": ["IP", "AUTO", "MCSI", "SP500"],
        "no_decimals": ["NHOME", "HSTART", "BPERM", "JOLTS_OPN", "JOLTS_QUT", "JOLTS_LAY"],
        "billions": ["FDEF", "USDEBT"]
    }
    
    if abbrev in format_types["yoy_growth"]:
        return f"{num:.2f}%"
    elif abbrev in format_types["percentage"]:
        return f"{num:.2f}%"
    elif abbrev in format_types["monetary"]:
        return f"${num:.2f}"
    elif abbrev in format_types["large_numbers"]:
        return f"{num:,.0f}"
    elif abbrev in format_types["hours"]:
        return f"{num:.1f} hrs"
    elif abbrev in format_types["decimal_2"]:
        return f"{num:.2f}"
    elif abbrev in format_types["no_decimals"]:
        return f"{num * 1000:,.0f}"
    elif abbrev in format_types["billions"]:
        return f"${num / 1000:.2f} B"
    else:
        return f"{num:.2f}"

# ----------------------------------------------------------------------------
# ✅ Function to Send Notification via LINE
def send_update_notification(updated_data):
    try:
        message = "📢 Macroeconomic Data Update 🚀\n"
        message += f"✅ {len(updated_data)} new data points were updated in the last 24 hours.\n\n"
        message += "🔹 Key Updates:\n"

        for indicator, abbrev, latest_value, previous_value in updated_data:
            formatted_latest = format_value(abbrev, latest_value)
            formatted_previous = format_value(abbrev, previous_value)
            message += f"- {indicator} ({abbrev}): {formatted_latest} (Previous: {formatted_previous})\n"

        message += "\n📊 Check the latest data by sending an abbreviation (e.g., 'CPI') to the bot!"

        # Initialize the synchronous LINE API client
        line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
        # Synchronously send the push message
        line_bot_api.push_message(USER_ID, TextSendMessage(text=message))
        log("✅ Notification sent successfully.")
    except Exception as e:
        log(f"❌ Failed to send notification: {e}")

# ----------------------------------------------------------------------------
# ✅ Main Execution
if __name__ == "__main__":
    log("auto_send_if_updated.py started.")
    new_data = check_new_updates()
    if not new_data:
        log("Exiting: No updates to process.")
    else:
        send_update_notification(new_data)
