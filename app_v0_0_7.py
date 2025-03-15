import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from indicator_handler import get_indicator_info_and_history
from credentials import LINE_ACCESS_TOKEN, LINE_SECRET, USER_ID, DB_CONFIG
import os

# Initialize Flask app
app = Flask(__name__)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)


# Home Route to Check Server Status
@app.route("/", methods=["GET"])
def home():
	return "LINE Bot is running!"

# Webhook Endpoint for LINE Messages
@app.route("/callback", methods=["POST"])
def callback():
	signature = request.headers.get("X-Line-Signature", None)
	body = request.get_data(as_text=True)

	print("===== Webhook Request Received =====")
	print("Signature:", signature)
	print("Body:", body)

	if not signature:
		print("❌ ERROR: Missing Signature in Request Headers")
		abort(400)

	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		print("❌ ERROR: Invalid Signature - Check LINE_SECRET")
		abort(400)

	return "OK"


# 🔹 LINE Bot Message Handling
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	user_message = event.message.text.strip().upper()  # Normalize input to uppercase

	if user_message in ["FFR", "CPI", "NFP", "GDP", "UR", "LFPR", "JOLTS", "AWH", "WAGE", "RTSAL", "IP",
						"ISMPMI", "AUTO", "NHOME", "XHOME", "MORTG", "HSTART", "BPERM", "HPI", "TBLNC",
						"FDEF", "USDEBT", "SP500", "10YY", "YCURV", "BSPRD", "PPI", "PCE", "M2", "V", "MCSI"]:
		messages = get_indicator_info_and_history(user_message)  # ✅ Fetch data

		if isinstance(messages, list):  
			# ✅ If multiple messages (JOLTS), send them as an array
			line_bot_api.reply_message(event.reply_token, messages)
		else:
			# ✅ If single message (CPI, FFR, etc.), send normally
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text=messages))
	else:
		reply_text = "I can provide macroeconomic data. Send an abbreviation (e.g., 'FFR') to get details."
		line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


# Flask server
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
