# 📌 auto_update.py - Fetches new data from FRED & updates MySQL database
import requests
import mysql.connector
from datetime import datetime
from credentials import DB_CONFIG  # ✅ Import DB_CONFIG

# Helper function to log messages with timestamp
def log(message):
	print(f"[{datetime.now()}] {message}")

# ✅ Function to Fetch Data from FRED API
def fetch_fred_data(series_id, api_key, last_recorded_date):
	url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
	response = requests.get(url)
	data = response.json()

	if "observations" in data:
		# 🔹 Ensure `last_recorded_date` is a string
		last_recorded_date = str(last_recorded_date)

		# 🔹 Filter data to only return new records after `last_recorded_date`
		recent_data = [
			(obs["date"], float(obs["value"]))
			for obs in data["observations"]
			if obs["value"] != "." and obs["date"] > last_recorded_date  # ✅ Ensures proper date comparison
		]
		return recent_data
	return []

# ✅ Function to Insert New Data into MySQL (Only If New)
def update_database():
	try:
		# 🔹 Connect to MySQL Database
		db = mysql.connector.connect(**DB_CONFIG)
		cursor = db.cursor()

		# 🔹 Fetch API Key from `data_sources` Table
		cursor.execute("SELECT api_key FROM data_sources WHERE source_name = 'FRED'")
		fred_api_key = cursor.fetchone()[0]  # Extract API Key

		# 🔹 Fetch List of Indicators & Their FRED Series IDs
		cursor.execute("SELECT indicator_id, fred_series_id FROM indicators WHERE source = 'FRED'")
		indicators = cursor.fetchall()

		updates_made = 0  # Counter to track updates

		# 🔹 Loop through Each Indicator & Fetch Data
		for indicator_id, series_id in indicators:
			# ✅ Fetch last recorded date for the indicator
			cursor.execute("""
				SELECT MAX(record_date) FROM indicator_data WHERE indicator_id = %s
			""", (indicator_id,))
			last_recorded_date = cursor.fetchone()[0]

			# ✅ If there's no existing data, set default start date
			last_recorded_date = last_recorded_date if last_recorded_date else "1900-01-01"

			log(f"🔄 Fetching data for {series_id} after {last_recorded_date}...")

			# ✅ Fetch only new data
			data = fetch_fred_data(series_id, fred_api_key, last_recorded_date)

			for record_date, value in data:
				try:
					# ✅ Insert new data if it's newer than the last recorded date
					cursor.execute("""
						INSERT INTO indicator_data (indicator_id, record_date, value) 
						VALUES (%s, %s, %s)
						ON DUPLICATE KEY UPDATE 
							value = VALUES(value), 
							last_updated = IF(value <> VALUES(value), NOW(), last_updated);
					""", (indicator_id, record_date, value))
					updates_made += 1
				except mysql.connector.Error as err:
					log(f"❌ Error inserting data for {series_id}: {err}")

		db.commit()
		log(f"✅ {updates_made} new data points updated in the database.")

	except mysql.connector.Error as err:
		log(f"❌ Database Connection Error: {err}")

	finally:
		if 'cursor' in locals() and cursor is not None:
			cursor.close()
		if 'db' in locals() and db.is_connected():
			db.close()
		log("✅ Database connection closed.")

# ✅ Run the `auto_update` function
if __name__ == "__main__":
	log("auto_update.py started.")
	update_database()
