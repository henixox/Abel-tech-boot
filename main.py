import telebot
from telebot import types
import threading
from flask import Flask
from threading import Thread

# 1. መሠረታዊ መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

# ዳታ ማስቀመጫ
user_counts = {}
user_registry = {}
ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. Keep Alive ክፍል (ቦቱ እንዳይዘጋ) ---
app = Flask('')

@app.route('/')
def home():
    return "Abel Tech Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- ለ. ግሩፑን የሚጠብቅ ክፍል ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def group_filter(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return 
    
    added = user_counts.get(uid, 0)
    if added < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id) # 50 ሰው ያልጨመረውን ጽሁፍ ያጠፋል
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ ግሩፑ ላይ ለመጻፍ 50 ሰው Add ማድረግ አለብዎት!\n📊 እስካሁን የጨመሩት፡ {added} ሰው ብቻ ነው።")
            threading.Timer(6, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

@bot.message_handler(content_types=['new_chat_members'])
def count_members(m):
    adder_id = m.from_user.id
    user_counts[adder_id] = user_counts.get(adder_id, 0) + len(m.new_chat_members)

# --- ሐ. የጥገና ምዝገባ (Private Chat) ---
@bot.message_handler(commands=['start'])
def welcome(m):
    if m.chat.type == 'private':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "ሰላም! የአቤል ቴክ ጥገና መመዝገቢያ ቦት ነው።", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def start_reg(m):
    uid = m.from_user.id
    added = user_counts.get(uid, 0)
    
    if uid in user_registry:
        bot.send_message(uid, "⚠️ ምዝገባ ላይ ነዎት። እባክዎ ጥያቄዎቹን ይመልሱ።")
        return

    if uid in ADMIN_IDS or added >= 50:
        user_registry[uid] = {'step': 'name'}
        msg = bot.send_message(uid, "✅ 50 ሰው ስለሞሉ ምዝገባ መጀመር ይችላሉ። ሙሉ ስምዎን ያስገቡ?")
        bot.register_next_step_handler(msg, process_name)
    else:
        bot.send_message(uid, f"❌ ይቆዩ! መጀመሪያ ግሩፑ ላይ 50 ሰው መሙላት አለብዎት።\n📊 እስካሁን የጨመሩት፡ {added} ሰው።")

def process_name(m):
    uid = m.from_user.id
    if m.text == '🛠️ ጥገና ለመመዝገብ' or not m.text:
        msg = bot.send_message(uid, "እባክዎ መጀመሪያ ስምዎን በትክክል ይጻፉ።")
        bot.register_next_step_handler(msg, process_name)
        return
    user_registry[uid]['name'] = m.text
    user_registry[uid]['username'] = m.from_user.username
    menu = "የሚጠገነውን ዕቃ በቁጥር ይምረጡ:\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(uid, menu)
    bot.register_next_step_handler(msg, process_item)

def process_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(uid, "አድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
    else:
        msg = bot.send_message(uid, "❌ ስህተት! እባክዎ ከ1-7 ያለውን ቁጥር ብቻ ይላኩ።")
        bot.register_next_step_handler(msg, process_item)

def process_loc(m):
    user_registry[m.from_user.id]['loc'] = m.text
    msg = bot.send_message(m.from_user.id, "ስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    uid = m.from_user.id
    if m.text.isdigit() and len(m.text) >= 10:
        user_registry[uid]['phone'] = m.text
        msg = bot.send_message(uid, "የዕቃውን ፎቶ ይላኩ?")
        bot.register_next_step_handler(msg, process_photo)
    else:
        msg = bot.send_message(uid, "❌ ስህተት፡ እባክዎ ትክክለኛ ስልክ ቁጥር ያስገቡ።")
        bot.register_next_step_handler(msg, process_phone)

def process_photo(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return
    photo_id = m.photo[-1].file_id if m.content_type == 'photo' else None
    link = f"https://t.me/{d['username']}" if d['username'] else f"tg://user?id={uid}"
    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n👤 ስም: [{d['name']}]({link})\n🛠️ ዕቃ: {d['item']}\n📍 አድራሻ: {d['loc']}\n📞 ስልክ: `{d['phone']}`")
    for aid in ADMIN_IDS:
        try:
            if photo_id: bot.send_photo(aid, photo_id, caption=summary, parse_mode='Markdown')
            else: bot.send_message(aid, summary, parse_mode='Markdown')
        except: pass
    bot.send_message(uid, "✅ ምዝገባዎ ተጠናቋል። በቅርቡ እንደውልልዎታለን!")
    user_registry.pop(uid, None)

# ቦቱን ማስነሳት
if __name__ == "__main__":
    keep_alive() # የዌብ ሰርቨሩን ያስነሳል
    print("Abel Tech Bot - Final Fix is Running...")
    bot.infinity_polling()
