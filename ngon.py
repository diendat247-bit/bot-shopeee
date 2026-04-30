import telebot
import re
import gspread
from google.oauth2.service_account import Credentials
import os
from flask import Flask
from threading import Thread

# --- CẤU HÌNH ---
TOKEN = "8652285031:AAEyRMV66gbQlcT6NALF_7AZC6vEPQ8RkWU"
bot = telebot.TeleBot(TOKEN)

# Kết nối Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("BotShopee").sheet1 

# Web server để Render không tắt bot
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- LỆNH /VIEW (Xem danh sách) ---
@bot.message_handler(commands=['view'])
def view_accounts(message):
    try:
        data = sheet.get_all_records()
        if not data:
            bot.reply_to(message, "📭 Danh sách trên Google Sheets đang trống.")
            return
        report = "📋 **DANH SÁCH TÀI KHOẢN:**\n\n"
        for row in data:
            report += f"👤: `{row.get('Username')}` | 🔑: `{row.get('Password')}`\n---\n"
        bot.reply_to(message, report, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi đọc dữ liệu: {e}")

# --- LỆNH /DEL (Xoá tài khoản) ---
@bot.message_handler(commands=['del'])
def delete_account(message):
    try:
        text = message.text.split()
        if len(text) < 2:
            bot.reply_to(message, "⚠️ Cú pháp: `/del tên_username`")
            return
        
        target = text[1]
        cell = sheet.find(target) # Tìm username trong Sheet
        
        if cell:
            sheet.delete_rows(cell.row) # Xoá cả hàng chứa username đó
            bot.reply_to(message, f"✅ Đã xoá tài khoản: `{target}`")
        else:
            bot.reply_to(message, f"❓ Không tìm thấy `{target}`")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi xoá: {e}")

# --- LƯU ACC TỰ ĐỘNG ---
@bot.message_handler(func=lambda message: True)
def handle_save(message):
    match = re.search(r'SPC_F=([^;| \n]+)', message.text)
    if match:
        spc_f = match.group(1)
        parts = message.text.split('|')
        name = parts[0].strip() if len(parts) > 0 else "Unknown"
        pwd = parts[1].strip() if len(parts) > 1 else "Unknown"
        try:
            sheet.append_row([name, pwd, spc_f])
            bot.reply_to(message, f"✅ Đã lưu acc `{name}` vào Google Sheets!")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi ghi Sheet: {e}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
