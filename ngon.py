import telebot
import re
import sqlite3
import os
from flask import Flask
from threading import Thread
import time

# 1. CẤU HÌNH TOKEN (Giữ nguyên của bạn)
TOKEN = "8759609630:AAEAJfmIIEZXcIR8OTRj2g_OmxCfxUXPKtc" # Thay bằng token đầy đủ của bạn
bot = telebot.TeleBot(TOKEN)

# 2. SERVER WEB PHỤ ĐỂ RENDER KHÔNG TẮT BOT
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy vĩnh viễn!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# 3. ĐƯỜNG DẪN DATABASE
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'shopee_final.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

with get_db() as conn:
    conn.execute("CREATE TABLE IF NOT EXISTS accounts (username TEXT, password TEXT, cookie TEXT)")

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🚀 Bot Shopee Online 24/7!\nMẫu: Tên | Pass | Cookie\nLệnh: /view")

@bot.message_handler(commands=['view'])
def view_accounts(message):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, cookie FROM accounts")
        rows = cursor.fetchall()
    
    if not rows:
        bot.reply_to(message, "📭 Danh sách trống.")
    else:
        report = f"📋 Danh sách ({len(rows)} acc):\n"
        for row in rows:
            report += f"👤: `{row[0]}` | 🔑: `{row[1]}`\n🍪: `{row[2]}`\n---\n"
        bot.reply_to(message, report, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    match = re.search(r'SPC_F=([^;| \n]+)', text)
    if match:
        spc_f = match.group(1)
        parts = text.split('|')
        name = parts[0].strip() if len(parts) > 0 else "NoName"
        pwd = parts[1].strip() if len(parts) > 1 else "NoPass"
        
        with get_db() as conn:
            conn.execute("INSERT INTO accounts VALUES (?, ?, ?)", (name, pwd, spc_f))
        bot.reply_to(message, f"✅ Đã lưu: {name}")

# 4. CHẠY BOT
if __name__ == "__main__":
    keep_alive() # Bật server web để Render thấy Port 8080
    print("Bot is starting...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            time.sleep(10)
