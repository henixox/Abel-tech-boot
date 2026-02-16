import telebot
from telebot import types
import threading
from flask import Flask
from threading import Thread
import os

API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') 
ADMIN_IDS = [8596054746, 7443150824] 
MY_PHONE = "09XXXXXXXX" 
bot = telebot.TeleBot(API_TOKEN)

user_counts = {}
user_registry = {}
registered_users = set()
ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. ዌብ ሰርቨር (ለ UptimeRobot) ---
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Bot is Running!"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=5000))
    t.daemon = True
   t.start()

# --- ለ. ሰላምታ እና የግሩፕ ጥበቃ ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_msg(m):
    for new_user in m.new_chat_members:
        bot.send_message(m.chat.id, f"እንኳን ደህና መጡ {new_user.first_name}! 🙏\n\nጥያቄ ለመጠየቅ መጀመሪያ 50 ሰው Add ያድርጉ።")
    user_counts[m.from_user.id] = user_counts.get(m.from_user.id, 0) + len(m.new_chat_members)
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def group_ctrl(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return
    if m.text and ("t.me/" in m.text or "http" in m.text):
        bot.delete_message(m.chat.id, m.message_id)
        return
    added = user_counts.get(uid, 0)
    if added < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            warn = bot.send_message(m.chat.id, f"⚠️ መጀመሪያ 50 ሰው Add ያድርጉ (ያለዎት፦ {added})።")
            threading.Timer(5, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

# --- ሐ. የምዝገባ ሂደት ከ "ማስተካከያ ቁልፍ" ጋር ---
@bot.message_handler(commands=['start'])
def start_reg(m):
    if m.chat.type == 'private':
        if m.from_user.id in registered_users:
            bot.send_message(m.chat.id, "❌ ቀድሞውኑ ተመዝግበዋል!")
            return
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "ሰላም! ጥገና ለመመዝገብ ከታች ያለውን ይጫኑ።", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def init_reg(m):
    uid = m.from_user.id
    added = user_counts.get(uid, 0)
    if uid in ADMIN_IDS or added >= 50:
        user_registry[uid] = {}
        msg = bot.send_message(uid, "✅ ምዝገባ ጀምረናል። ሙሉ ስምዎን ያስገቡ?")
        bot.register_next_step_handler(msg, get_name)
    else:
        bot.send_message(uid, f"❌ መጀመሪያ 50 ሰው ይጨምሩ። (ያለዎት፦ {added})")

def get_name(m):
    user_registry[m.from_user.id]['name'] = m.text
    menu = "የሚጠገነውን ዕቃ ቁጥር ይላኩ:\n" + "\n".join([f"{k}. {v}" for k, v in ITEMS.items()])
    msg = bot.send_message(m.from_user.id, menu)
    bot.register_next_step_handler(msg, get_item)

def get_item(m):
    if m.text in ITEMS:
        user_registry[m.from_user.id]['item'] = ITEMS[m.text]
        msg = bot.send_message(m.from_user.id, "አድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, get_loc)
    else:
        msg = bot.send_message(m.from_user.id, "⚠️ ከ1-7 ያለውን ቁጥር ብቻ ይላኩ።")
        bot.register_next_step_handler(msg, get_item)

def get_loc(m):
    user_registry[m.from_user.id]['loc'] = m.text
    msg = bot.send_message(m.from_user.id, "ስልክ ቁጥርዎን ያስገቡ (ቁጥር ብቻ)?")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(m):
    uid = m.from_user.id
    if m.text and m.text.isdigit() and len(m.text) >= 10:
        user_registry[uid]['phone'] = m.text
        # ስልኩን ለማረጋገጥ ቁልፍ ማሳየት
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ ትክክል ነው - ቀጥል", callback_data="confirm_phone"))
        kb.add(types.InlineKeyboardButton("❌ ተሳስቻለሁ - አስተካክል", callback_data="edit_phone"))
        bot.send_message(uid, f"ያስገቡት ስልክ፡ {m.text}\nትክክል መሆኑን ያረጋግጡ?", reply_markup=kb)
    else:
        msg = bot.send_message(uid, "❌ ስህተት! ትክክለኛ ስልክ ቁጥር ብቻ ያስገቡ።")
        bot.register_next_step_handler(msg, get_phone)

# --- መ. የቁልፎች ስራ (Callback Handler) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    uid = call.message.chat.id
    if call.data == "confirm_phone":
        bot.edit_message_text("✅ ስልክዎ ተረጋግጧል። አሁን የዕቃውን ፎቶ ይላኩ?", uid, call.message.message_id)
        bot.register_next_step_handler(call.message, finish_reg)
    elif call.data == "edit_phone":
        msg = bot.edit_message_text("🔄 እሺ፣ ትክክለኛውን ስልክ ቁጥር አሁን ይጻፉ?", uid, call.message.message_id)
        bot.register_next_step_handler(call.message, get_phone)

def finish_reg(m):
    uid = m.from_user.id
    if m.content_type != 'photo':
        msg = bot.send_message(uid, "⚠️ እባክዎ ፎቶ ይላኩ።")
        bot.register_next_step_handler(msg, finish_reg)
        return
    d = user_registry[uid]
    summary = f"🚨 **አዲስ ትዕዛዝ**\n\n👤 ስም: {d['name']}\n🛠️ ዕቃ: {d['item']}\n📍 አድራሻ: {d['loc']}\n📞 ስልክ: {d['phone']}"
    for aid in ADMIN_IDS: bot.send_photo(aid, m.photo[-1].file_id, caption=summary)
    bot.send_message(uid, f"እናመሰግናለን! 🙏 በ {MY_PHONE} እንገናኝ።")
    registered_users.add(uid)
    user_registry.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
