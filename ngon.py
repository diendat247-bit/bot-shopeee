import telebot
import re
import gspread
from google.oauth2.service_account import Credentials
import os
import time
from flask import Flask
from threading import Thread

# 1. CẤU HÌNH BOT (Thay Token của bạn vào đây)
TOKEN = "8759609630:AAEUXLo11XxmWuJU42mjZz959NtSThn9vR8"
bot = telebot.TeleBot(TOKEN)

# 2. CẤU HÌNH GOOGLE SHEETS
# File service_account.json là file bạn tải từ Google Cloud về
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)
# "BotShopee" là tên file Google Sheet bạn đã tạo
sheet = client.open("BotShopee").sheet1 

# 3. SERVER GIỮ THỨC (Cho Render)
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# 4. XỬ LÝ LỆNH /VIEW (Lấy dữ liệu từ Google Sheets)
@bot.message_handler(commands=['view'])
def view_accounts(message):
    try:
        data = sheet.get_all_records()
        if not data:
            bot.reply_to(message, "📭 Google Sheets đang trống.")
            return
        report = "📋 Danh sách từ Google Sheets:\n\n"
        for row in data:
            report += f"👤: `{row['Username']}` | 🔑: `{row['Password']}`\n🍪: `{row['Cookie']}`\n---\n"
        bot.reply_to(message, report, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi đọc Sheet: {e}")

# 5. LƯU ACC MỚI VÀO GOOGLE SHEETS
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    match = re.search(r'SPC_F=([^;| \n]+)', text)
    if match:
        spc_f = match.group(1)
        parts = text.split('|')
        name = parts[0].strip() if len(parts) > 0 else "NoName"
        pwd = parts[1].strip() if len(parts) > 1 else "NoPass"
        
        try:
            # Ghi một hàng mới vào Google Sheets
            sheet.append_row([name, pwd, spc_f])
            bot.reply_to(message, f"✅ Đã lưu vào Google Sheets: {name}")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi ghi Sheet: {e}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
