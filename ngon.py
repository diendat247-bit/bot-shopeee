import telebot
import re
import gspread
from google.oauth2.service_account import Credentials
import os
import time
from flask import Flask
from threading import Thread

# 1. CẤU HÌNH BOT
TOKEN = "8652285031:AAEyRMV66gbQlcT6NALF_7AZC6vEPQ8RkWU"
bot = telebot.TeleBot(TOKEN)

# 2. CẤU HÌNH GOOGLE SHEETS
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("BotShopee").sheet1 

# 3. SERVER GIỮ THỨC
app = Flask('')
@app.route('/')
def home(): return "Bot is Live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- CÁC TÍNH NĂNG CHÍNH ---

# Lệnh xem danh sách
@bot.message_handler(commands=['view'])
def view_accounts(message):
    try:
        data = sheet.get_all_records()
        if not data:
            bot.reply_to(message, "📭 Danh sách trống.")
            return
        report = "📋 **DANH SÁCH ACC:**\n\n"
        for row in data:
            report += f"👤: `{row['Username']}` | 🔑: `{row['Password']}`\n---\n"
        bot.reply_to(message, report, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {e}")

# LỆNH XOÁ TÀI KHOẢN (MỚI)
@bot.message_handler(commands=['del'])
def delete_account(message):
    try:
        # Lấy tên username cần xoá sau lệnh /del
        cmd_parts = message.text.split()
        if len(cmd_parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập theo cú pháp: `/del username`", parse_mode="Markdown")
            return
        
        target_user = cmd_parts[1]
        
        # Tìm ô có chứa username đó
        cell = sheet.find(target_user)
        
        if cell:
            # Xoá toàn bộ hàng chứa ô đó
            sheet.delete_rows(cell.row)
            bot.reply_to(message, f"✅ Đã xoá tài khoản: `{target_user}`", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❓ Không tìm thấy tài khoản `{target_user}` trong danh sách.", parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi xoá: {e}")

# Lưu acc tự động khi gửi định dạng SPC_F
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
            sheet.append_row([name, pwd, spc_f])
            bot.reply_to(message, f"✅ Đã lưu vào Google Sheets: `{name}`", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi ghi Sheet: {e}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
