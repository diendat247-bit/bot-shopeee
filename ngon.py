import telebot
import re
import gspread
from google.oauth2.service_account import Credentials
import os
from flask import Flask
from threading import Thread

# --- 1. CẤU HÌNH BOT ---
TOKEN = "8652285031:AAEyRMV66gbQlcT6NALF_7AZC6vEPQ8RkWU"
bot = telebot.TeleBot(TOKEN)

# --- 2. THÔNG TIN XÁC THỰC GOOGLE (Dán trực tiếp từ JSON của bạn) ---
info = {
  "type": "service_account",
  "project_id": "shopee-acc",
  "private_key_id": "2d9b962d2917b75ed73bd45f4edfbe84a9ea28ee",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQD4KyaCFAnnsd+o\ngbHa3ustw+kwVVS1D7ScQijIySY+97EJUrD7tqtadYxerezgu+EMomDhPxAs3Kxd\nn1r+WYCY05o/dXPhaWLySSQViSsWAqWtWkLmtav4AUERJPJtsZDK9fvvVRWk/BVZ\n2/ou1SAxixEkn+esDDrrAJa/EV7j6gdGKOMGu9+VBFBI73skYsKLg8cs389FBkqu\nnhwjnrdc9piufPksU1jig9hNUFqXySgaELV+oWlKptd2xT7SYlFy29La6VUgpjMY\nGBXL8+BKiXWtJfF6/71Sxc3EqNZ8cRiTl0OQW3zM38sDISOQCzmmDHTfw/xLrk11\n1QpIXSKJAgMBAAECggEADpTkfJimU1eTe3BxbZmTCnucKEOfSEs9sr+9azzMcz81\nBwX1kbi0PUqyXn7MMBFCAi7JT/rXXbdypkaef1rtcC1gvxFM54X8cx2CkgRfBHpP\n1016KFms2tPiCZqY5wKbrh1BehjO/oR0UbUX8GgD7f1MmtENeQG39YZxlRT1dSE1\nwD+CkQVbuyAZrMHKK4VEubGbArBKH90o0yQ3I7ig1jv84rJwuMqf0x1Vx2wjBUog\n/T7oKWdoUKPSNzmQT3UfG0Cf2F9VcKxviJQbW2QkHT8qPstZw44mdqNI/rcp6x9y\nqK5Mp2j1zN30MTrpQkk8aemY4o58AaVzjWGtPL9JPQKBgQD/b8A7ruDbW21lhvMK\nqG0ikPk9713WECTAvzYWaBOAj12GqGH8hqHgxMZAU7jSO3GRWWUyCR3o6E6ysNkG\nUyFSe4A5tZaUXVmht49RqaH5BfzaAuwN9QynaEiNmI5jNuCBwBdTW/oz++NlRTut\nE6OPvRNWYPsdcUXckKKT09wEhQKBgQD4t0uQbAVQi7RIDluk93OBkPs1Aae/MSwm\nk5xS67UxU934M1LixVkkXjdTnaeocUYJPY+DxVGo5qGuRLuBNXLJIBhUfPuK/wpF\n4zFD8WxyBSh45fgaNbJVEemOJ2foaHWYkA7ZZ4u8I2vqJGcIvybZN7w4Q0sRiTAr\nKxYRT1tXNQKBgAWH2uav66h0O1Mmb968NNi5wNvJcgOvh8wwl7A2gq2W7RR8UtrP\n43Nlb1F3Ppo2tUfLYriJn/8qAII3+Ar+A8uwZt9ZAjCmMMmimtTO0nX83jOuOoQ2\n2RZK2L9QHU0ipAvLJ/YjGLDFdG/95sPhl/oFwwRsxyMlD7kt3IdM4AetAoGBAKai\nB1pnRNhGAS8Vj4ji0NxJykQlK8IIq8/cratQiEDYM6sKl8me9q5LAT5gLefInGes\neu6J0MAcZM5g9k8HBDSD8EkKw2zImpVgNa2Tnlh15Du7t5G30Bb2vUekVxV6hu8D\n9S7rFM+j27UvVmihyOFXWh9H1o+VHlSNtWc7h7LRAoGBALlANcSbr0av8LM2VH1l\nhFrsOo7YZ8uW84Prd28Qz0MGiEgwYYXoWjDQLkx0k04y8H5/TQ5Nz0a03c/GiqJB\nwnYwGyUxKhOqtMutNbXR27SaTq2bSM1GnG/OISioZEKtXD+UaBbKXjYPcb8A2qHT\ndfj8wF914oOA+u3ud5yntJhe\n-----END PRIVATE KEY-----\n",
  "client_email": "bot-shopee@shopee-acc.iam.gserviceaccount.com",
  "client_id": "116972470211500611365",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bot-shopee%40shopee-acc.iam.gserviceaccount.com"
}

# Kết nối Google Sheets bằng thông tin trên
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)
# Đảm bảo tên file Sheet của bạn đúng là BotShopee
sheet = client.open("BotShopee").sheet1 

# --- 3. SERVER GIỮ THỨC ---
app = Flask('')
@app.route('/')
def home(): return "Bot Live!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): Thread(target=run).start()

# --- 4. LỆNH XỬ LÝ ---
@bot.message_handler(commands=['view'])
def view_accounts(message):
    try:
        data = sheet.get_all_records()
        if not data:
            bot.reply_to(message, "📭 Danh sách trống.")
            return
        report = "📋 **DANH SÁCH ACC:**\n\n"
        for row in data:
            report += f"👤: `{row.get('Username')}` | 🔑: `{row.get('Password')}`\n---\n"
        bot.reply_to(message, report, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi đọc: {e}")

@bot.message_handler(commands=['del'])
def delete_account(message):
    try:
        text = message.text.split()
        if len(text) < 2:
            bot.reply_to(message, "⚠️ Cú pháp: `/del username`")
            return
        target = text[1]
        cell = sheet.find(target)
        if cell:
            sheet.delete_rows(cell.row)
            bot.reply_to(message, f"✅ Đã xoá acc: `{target}`")
        else:
            bot.reply_to(message, f"❓ Không thấy `{target}`")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi xoá: {e}")

@bot.message_handler(func=lambda message: True)
def handle_save(message):
    match = re.search(r'SPC_F=([^;| \n]+)', message.text)
    if match:
        spc_f = match.group(1)
        parts = message.text.split('|')
        name = parts[0].strip() if len(parts) > 0 else "N/A"
        pwd = parts[1].strip() if len(parts) > 1 else "N/A"
        try:
            sheet.append_row([name, pwd, spc_f])
            bot.reply_to(message, f"✅ Đã lưu acc `{name}`!")
        except Exception as e:
            bot.reply_to(message, f"❌ Lỗi ghi: {e}")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
