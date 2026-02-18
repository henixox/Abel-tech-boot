import telebot
from telebot import types
import sqlite3
from flask import Flask
from threading import Thread
import re

# 1. መሠረታዊ መቼቶች (Token እና ID)
API_TOKEN = '7948646187:AAGH1rAb3-PD27GoDvZLDQcAkvrjO-q_ptQ'
MY_ADMIN_ID = 8596054746 
bot = telebot.TeleBot(API_TOKEN)
app = Flask('')

# 2. ዳታቤዝ
def init_db():
    conn = sqlite3.connect('abel_tech.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS repairs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, item TEXT, phone TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- 3. Abel Tech ሰላምታ ---
@bot.message_handler(commands=['start'])
def welcome(m):
    welcome_text = (
        "እንኳን ወደ Abel Tech የጥገና አገልግሎት በሰላም መጡ! 🛠️\n\n"
        "📞 ስልክ፦ 0983664175\n"
        "📍 አድራሻ፦ አዲሱ ገበያ፣ አራብሳ፣ ሰሚት 72\n\n"
        "ለመመዝገብ /repair ይበሉ።"
    )
    bot.reply_to(m, welcome_text)

# --- 4. የጥገና ምዝገባ (በምርጫ እና በቁጥር ቁጥጥር) ---
@bot.message_handler(commands=['repair'])
def start_repair(m):
    msg = bot.send_message(m.chat.id, "ስምዎን ያስገቡ፦")
    bot.register_next_step_handler(msg, get_name)

def get_name(m):
    user_data = {'name': m.text}
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('ቴሌቪዥን', 'ኤር ኮንዲሽነር', 'ሂት ፓምፕ', 'ጄኔሬተር', 'ፍሪጅ', 'ምድጃ (ኦቨን)', 'የልብስ ማጠቢያ ማሽን')
    msg = bot.send_message(m.chat.id, "የሚጠገነውን ዕቃ ይምረጡ፦", reply_markup=markup)
    bot.register_next_step_handler(msg, get_item, user_data)

def get_item(m, user_data):
    user_data['item'] = m.text
    msg = bot.send_message(m.chat.id, "ስልክ ቁጥርዎን ያስገቡ (ቁጥር ብቻ)፦", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_phone, user_data)

def get_phone(m, user_data):
    phone = m.text
    if not phone.isdigit():
        msg = bot.send_message(m.chat.id, "⚠️ ስህተት! እባክዎ ቁጥር ብቻ ያስገቡ፦")
        bot.register_next_step_handler(msg, get_phone, user_data)
        return

    c = conn.cursor()
    c.execute("INSERT INTO repairs (user_id, name, item, phone) VALUES (?, ?, ?, ?)", (m.from_user.id, user_data['name'], user_data['item'], phone))
    conn.commit()
    bot.send_message(MY_ADMIN_ID, f"🔔 አዲስ ጥያቄ!\n👤 ስም: {user_data['name']}\n🛠 ዕቃ: {user_data['item']}\n📞 ስልክ: {phone}")
    bot.reply_to(m, "✅ ተመዝግቧል! እናመሰግናለን።")

@app.route('/')
def home(): return "Online"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
