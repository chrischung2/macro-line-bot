# 📌 indicator_handler.py - Handles SQL queries for macroeconomic indicators
import mysql.connector
from linebot.models import TextSendMessage

# ✅ Define reusable SQL query templates for different data formats
query_templates = {
	"yoy_growth": """
		SELECT i.indicator_name, i.category, i.note, 
		recent.record_date AS recent_date,
		CONCAT(ROUND(((recent.value - past.value) / past.value) * 100, 2), '%') AS formatted_value
		FROM indicator_data recent
		JOIN indicator_data past
			ON recent.indicator_id = past.indicator_id
			AND DATE_SUB(recent.record_date, INTERVAL 12 MONTH) = past.record_date
		JOIN indicators i ON recent.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY recent.record_date DESC
		LIMIT 15;
	""",
	"percentage": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		CONCAT(ROUND(d.value, 2), '%') AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"monetary": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		CONCAT('$', ROUND(d.value, 2)) AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"large_numbers": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		FORMAT(d.value, 0) AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"hours": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		CONCAT(ROUND(d.value, 1), ' hrs') AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"decimal_2": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		ROUND(d.value, 2) AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"no_decimals": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		FORMAT(d.value * 1000, 0) AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	""",
	"billions": """
		SELECT i.indicator_name, i.category, i.note, d.record_date, 
		CONCAT('$', ROUND(d.value / 1000, 2), ' B') AS formatted_value
		FROM indicator_data d
		JOIN indicators i ON d.indicator_id = i.indicator_id
		WHERE i.abbreviation = %s
		ORDER BY d.record_date DESC
		LIMIT 15;
	"""
}


# Function to Fetch Indicator Info and Historical Data
def get_indicator_info_and_history(user_input):
	try:
		db = mysql.connector.connect(
			host="localhost",
			user="root",
			password="@Ri2aoei9ie",
			database="macroeconomic_db"
		)
		cursor = db.cursor()
	except mysql.connector.Error as err:
		print(f"❌ Database Connection Error: {err}")
		return "⚠️ Error: Unable to connect to the database. Please try again later."

	try:
		# ✅ Define indicator categories
		format_types = {
			"yoy_growth": ["CPI", "HPI", "PPI", "PCE"],
			"percentage": ["GDP", "FFR", "MORTG", "UR", "LFPR", "V"],
			"monetary": ["WAGE"],
			"large_numbers": ["NFP", "RTSAL", "XHOME", "TBLNC", "M2"],
			"hours": ["AWH"],
			"decimal_2": ["IP", "AUTO", "MCSI"],
			"no_decimals": ["NHOME", "HSTART", "BPERM"],
			"billions": ["FDEF", "USDEBT"]
		}

		# ✅ Special Handling for JOLTS (3 Messages)
		if user_input == "JOLTS":
			# ✅ Special handling for JOLTS (Multiple Messages)
			query = """
			SELECT 
				ANY_VALUE(i.indicator_name) AS indicator_name,
				ANY_VALUE(i.category) AS category,
				ANY_VALUE(i.note) AS note,
				d.record_date,
				MAX(CASE WHEN i.abbreviation = 'JOLTS_OPN' THEN d.value END) AS Job_Openings,
				MAX(CASE WHEN i.abbreviation = 'JOLTS_QUT' THEN d.value END) AS Job_Quits,
				MAX(CASE WHEN i.abbreviation = 'JOLTS_LAY' THEN d.value END) AS Job_Layoffs
			FROM indicator_data d
			JOIN indicators i ON d.indicator_id = i.indicator_id
			WHERE i.abbreviation IN ('JOLTS_OPN', 'JOLTS_QUT', 'JOLTS_LAY')
			GROUP BY d.record_date 
			ORDER BY d.record_date DESC
			LIMIT 24;
			"""
			
			cursor.execute(query)
			results = cursor.fetchall()

			if results:
				indicator_name = results[0][0]  
				category = results[0][1]  
				note = results[0][2] if results[0][2] else "No description available."

				# 📊 First Message: JOLTS Explanation
				messages = [
					TextSendMessage(text=(
						f"📊 {indicator_name}\n📌 Category: {category}\n📝 {note}\n\n"
						"🔹 Openings high = Strong labor demand\n"
						"🔹 Quits high & Layoffs low = Strong labor market\n"
						"🔹 Layoffs high & Openings low = Weak labor market"
					))
				]

				# 📈 Second Message: Job Openings
				job_openings_msg = "📈 **Job Openings (Unit: Thousands of persons)**\n\nDate            | Job Openings\n----------|------------\n"
				for row in results:
					_, _, _, date, job_open, _, _ = row
					job_openings_msg += f"{date} | {int(job_open):,}\n" if job_open is not None else f"{date} | N/A\n"
				messages.append(TextSendMessage(text=job_openings_msg))

				# 📉 Third Message: Job Quits
				job_quits_msg = "📉 **Job Quits (Unit: Thousands of persons)**\n\nDate            | Job Quits\n----------|---------\n"
				for row in results:
					_, _, _, date, _, job_quit, _ = row
					job_quits_msg += f"{date} | {int(job_quit):,}\n" if job_quit is not None else f"{date} | N/A\n"
				messages.append(TextSendMessage(text=job_quits_msg))

				# 🔻 Fourth Message: Job Layoffs
				job_layoffs_msg = "🔻 **Job Layoffs (Unit: Thousands of persons)**\n\nDate            | Job Layoffs\n----------|---------\n"
				for row in results:
					_, _, _, date, _, _, job_lay = row
					job_layoffs_msg += f"{date} | {int(job_lay):,}\n" if job_lay is not None else f"{date} | N/A\n"
				messages.append(TextSendMessage(text=job_layoffs_msg))

				# ✅ Return JOLTS Messages Instead of Standard Response
				return messages  

			else:
				return [TextSendMessage(text="No JOLTS data available.")]


		# ✅ Special Handling for SP500 (Requires Current Position Calculation)
		elif user_input == "SP500":
			query_recent = """
			SELECT 
				i.indicator_name,
				i.category,
				i.note,
				d.record_date,
				FORMAT(d.value, 2) AS formatted_value  -- ✅ SP500 should NOT have '%'
			FROM indicator_data d
			JOIN indicators i
				ON d.indicator_id = i.indicator_id
			WHERE i.abbreviation = %s
			ORDER BY d.record_date DESC
			LIMIT 15;
			"""

			cursor.execute(query_recent, (user_input,))
			results = cursor.fetchall()

			# ✅ Fetch the 52-week high and low separately
			query_high_low = """
			SELECT 
				FORMAT(MAX(d.value), 2) AS high_52w,
				FORMAT(MIN(d.value), 2) AS low_52w
			FROM indicator_data d
			JOIN indicators i
				ON d.indicator_id = i.indicator_id
			WHERE i.abbreviation = %s
			AND d.record_date >= DATE_SUB(CURDATE(), INTERVAL 52 WEEK);
			"""

			cursor.execute(query_high_low, (user_input,))
			high_low_result = cursor.fetchone()
			high_52w, low_52w = high_low_result if high_low_result else ("N/A", "N/A")

			if results:
				indicator_name, category, note = results[0][:3]
				note = note if note else "No description available."
				
				latest_date, latest_value = results[0][3], results[0][4]

				# ✅ Calculate percentage drop from 52-week high
				try:
					high_52w_float = float(high_52w.replace(',', '')) if high_52w != "N/A" else None
					latest_value_float = float(latest_value.replace(',', ''))
					percent_drop = round(((high_52w_float - latest_value_float) / high_52w_float) * 100, 2) if high_52w_float else "N/A"
				except Exception:
					percent_drop = "N/A"

				response = f"📊 {indicator_name}\n📌 Category: {category}\n📝 {note}\n\n"
				response += f"🔹 52W Highs and Lows: [H] {high_52w} / [L] {low_52w}\n"
				response += f"🔹 Current position: -{percent_drop}% from 52-week High\n\n"
				response += "🔹 Last 15 Data Points:\n"
				response += "\n".join(f"{date}: {formatted_value}" for _, _, _, date, formatted_value in results)
			else:
				response = f"Not enough historical data available for {user_input}."

		# ✅ Special Handling for Interest Rate Indicators (10YY, YCURV, BSPRD) - Adds "%"
		elif user_input in ["10YY", "YCURV", "BSPRD"]:
			query_recent = """
			SELECT 
				i.indicator_name,
				i.category,
				i.note,
				d.record_date,
				CONCAT(FORMAT(d.value, 2), '%') AS formatted_value  -- ✅ Adds '%' for interest rates
			FROM indicator_data d
			JOIN indicators i
				ON d.indicator_id = i.indicator_id
			WHERE i.abbreviation = %s
			ORDER BY d.record_date DESC
			LIMIT 15;
			"""

			cursor.execute(query_recent, (user_input,))
			results = cursor.fetchall()

			# ✅ Fetch the 52-week high and low separately
			query_high_low = """
			SELECT 
				CONCAT(FORMAT(MAX(d.value), 2), '%') AS high_52w,  -- ✅ Adds '%' to high
				CONCAT(FORMAT(MIN(d.value), 2), '%') AS low_52w  -- ✅ Adds '%' to low
			FROM indicator_data d
			JOIN indicators i
				ON d.indicator_id = i.indicator_id
			WHERE i.abbreviation = %s
			AND d.record_date >= DATE_SUB(CURDATE(), INTERVAL 52 WEEK);
			"""

			cursor.execute(query_high_low, (user_input,))
			high_low_result = cursor.fetchone()
			high_52w, low_52w = high_low_result if high_low_result else ("N/A", "N/A")

			if results:
				indicator_name, category, note = results[0][:3]
				note = note if note else "No description available."

				response = f"📊 {indicator_name}\n📌 Category: {category}\n📝 {note}\n\n"
				response += f"🔹 52W Highs and Lows: [H] {high_52w} / [L] {low_52w}\n\n"
				response += "🔹 Last 15 Data Points:\n"
				response += "\n".join(f"{date}: {formatted_value}" for _, _, _, date, formatted_value in results)
			else:
				response = f"Not enough historical data available for {user_input}."

		# ✅ Add this elif to ensure general inputs are handled in the same if-elif structure
		elif any(user_input in values for values in format_types.values()): 
			# ✅ Dynamically select the query type
			query = None
			if user_input in format_types["yoy_growth"]:
				query = query_templates["yoy_growth"]
			elif user_input in format_types["percentage"]:
				query = query_templates["percentage"]
			elif user_input in format_types["monetary"]:
				query = query_templates["monetary"]
			elif user_input in format_types["large_numbers"]:
				query = query_templates["large_numbers"]
			elif user_input in format_types["hours"]:
				query = query_templates["hours"]
			elif user_input in format_types["decimal_2"]:
				query = query_templates["decimal_2"]
			elif user_input in format_types["no_decimals"]:
				query = query_templates["no_decimals"]
			elif user_input in format_types["billions"]:
				query = query_templates["billions"]

			# ✅ If a query is found, execute it
			if query:
				try: # ✅ Catch SQL errors when executing the query
					cursor.execute(query, (user_input,))
					results = cursor.fetchall()
				except mysql.connector.Error as err:
					print(f"❌ SQL Query Error: {err}")
					return f"⚠️ Error: Unable to fetch data for {user_input}. Please try again later."

				if results:
					indicator_name, category, note = results[0][:3]
					note = note if note else "No description available."

					response = f"📊 {indicator_name}\n📌 Category: {category}\n📝 {note}\n\n🔹 Last 15 Data Points:\n"
					response += "\n".join(f"{date}: {formatted_value}" for _, _, _, date, formatted_value in results)
				else:
					response = f"Not enough historical data available for {user_input}."
			else:
				response = f"Invalid input: {user_input} is not recognized."
		else:
			response = f"Invalid input: {user_input} is not recognized.(Final)"

	except mysql.connector.Error as err:
		print(f"❌ SQL Execution Error: {err}")
		return f"⚠️ Database error: Unable to process your request at this time. Please try again later."

	finally:
		# ✅ Check if `cursor` exists before closing
		if 'cursor' in locals() and cursor is not None:
			cursor.close()
			print("✅ Cursor closed successfully.")

		# ✅ Check if `db` exists before closing
		if 'db' in locals() and 'is_connected' in dir(db) and db.is_connected():
			db.close()
			print("✅ Database connection closed successfully.")

	return response
