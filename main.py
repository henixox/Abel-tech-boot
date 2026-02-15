import telebot
from telebot import types
import threading
from flask import Flask
from threading import Thread
import os

# 1. መሠረታዊ መቼቶች
API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') # በ Secrets ውስጥ ያስገባኸው Token
ADMIN_IDS = [8596054746, 7443150824] 
MY_PHONE = "+2519XXXXXXXX" # የአንተን ስልክ እዚህ ጋር ቀይረው
bot = telebot.TeleBot(API_TOKEN)

user_counts = {}
user_registry = {}
registered_users = set()
ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. ዌብ ሰርቨር (ለ UptimeRobot) ---
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Bot is Fully Fixed!"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    t.daemon = True
    t.start()

# --- ለ. አዲስ ሰው ሲገባ ሰላምታ መስጠት ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(m):
    for new_user in m.new_chat_members:
        welcome_msg = (f"እንኳን ደህና መጡ {new_user.first_name} ወደ አቤል ቴክ ጥገና! 🙏\n\n"
                       f"🛠 ዕቃ ለማስጠገን መጀመሪያ 50 ሰው Add ማድረግ እንዳለብዎ አይርሱ።")
        bot.send_message(m.chat.id, welcome_msg)
    # የጨመረውን ሰው መቁጠር
    user_counts[m.from_user.id] = user_counts.get(m.from_user.id, 0) + len(m.new_chat_members)

# --- ሐ. ግሩፕ ጥበቃ (50 ሰው እና ሊንክ መከልከል) ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def group_control(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return

    if m.text and ("t.me/" in m.text or "http" in m.text):
        bot.delete_message(m.chat.id, m.message_id)
        return

    added = user_counts.get(uid, 0)
    if added < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ ለመጻፍ መጀመሪያ 50 ሰው Add ያድርጉ (ያለዎት፦ {added})።")
            threading.Timer(5, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

# --- መ. ምዝገባ (Private Chat) ---
@bot.message_handler(commands=['start'])
def start_reg(m):
    if m.chat.type == 'private':
        if m.from_user.id in registered_users:
            bot.send_message(m.chat.id, "❌ ቀድሞውኑ ተመዝግበዋል! በቅርቡ እንደውልልዎታለን።")
            return
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "ሰላም! ጥገና ለመመዝገብ ከታች ያለውን ይጫኑ።", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def init_process(m):
    uid = m.from_user.id
    if uid in registered_users: return
    
    added = user_counts.get(uid, 0)
    if uid in ADMIN_IDS or added >= 50:
        user_registry[uid] = {}
        msg = bot.send_message(uid, "✅ ምዝገባ ጀምረናል። ሙሉ ስምዎን ያስገቡ?")
        bot.register_next_step_handler(msg, get_name)
    else:
        bot.send_message(uid, f"❌ መጀመሪያ 50 ሰው ግሩፑ ላይ ይጨምሩ። (ያለዎት፦ {added})")

def get_name(m):
    uid = m.from_user.id
    user_registry[uid]['name'] = m.text
    menu = "የሚጠገነውን ዕቃ ቁጥር ይላኩ:\n" + "\n".join([f"{k}. {v}" for k, v in ITEMS.items()])
    msg = bot.send_message(uid, menu)
    bot.register_next_step_handler(msg, get_item)

def get_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(uid, "አድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, get_loc)
    else:
        msg = bot.send_message(uid, "⚠️ እባክዎ ከ1-7 ያለውን ቁጥር ብቻ ይላኩ።")
        bot.register_next_step_handler(msg, get_item)

def get_loc(m):
    user_registry[m.from_user.id]['loc'] = m.text
    msg = bot.send_message(m.from_user.id, "ስልክ ቁጥርዎን ያስገቡ (ቁጥር ብቻ)?")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(m):
    uid = m.from_user.id
    # ቁጥር ብቻ መሆኑን እና ርዝመቱን ማረጋገጥ
    if m.text and m.text.isdigit() and len(m.text) >= 10:
        user_registry[uid]['phone'] = m.text
        msg = bot.send_message(uid, "የዕቃውን ፎቶ ይላኩ?")
        bot.register_next_step_handler(msg, finish_reg)
    else:
        msg = bot.send_message(uid, "❌ ስህተት! እባክዎ ትክክለኛ ስልክ ቁጥር ብቻ ያስገቡ (ቁጥር ብቻ)።")
        bot.register_next_step_handler(msg, get_phone)

def finish_reg(m):
    uid = m.from_user.id
    if m.content_type != 'photo':
        msg = bot.send_message(uid, "⚠️ እባክዎ የዕቃውን ፎቶ ይላኩ።")
        bot.register_next_step_handler(msg, finish_reg)
        return

    d = user_registry[uid]
    summary = f"🚨 **አዲስ ትዕዛዝ**\n\n👤 ስም: {d['name']}\n🛠️ ዕቃ: {d['item']}\n📍 አድራሻ: {d['loc']}\n📞 ስልክ: {d['phone']}"
    
    for aid in ADMIN_IDS:
        bot.send_photo(aid, m.photo[-1].file_id, caption=summary)
    
    # የምስጋና መልእክት ከአንተ ስልክ ጋር
    thanks_msg = (f"ተመዝግበው ጨርሰዋል፣ እናመሰግናለን! 🙏\n"
                  f"መረጃዎ ለአድሚን ደርሷል፤ በቅርቡ እንደውልልዎታለን።\n\n"
                  f"ለተጨማሪ መረጃ በ {MY_PHONE} ይደውሉልን።")
    bot.send_message(uid, thanks_msg)
    registered_users.add(uid)
    user_registry.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
