import telebot
from telebot import types
from flask import Flask
from threading import Thread
import threading

# 1. ሰርቨር እንዳይዘጋ (Keep-Alive)
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Master System is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] # ያንተ እና የአቤል ID
bot = telebot.TeleBot(API_TOKEN)

# ዳታቤዝ (በሜሞሪ ላይ)
user_counts = {}       
registered_users = set() 
user_registry = {}      

ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. ግሩፕ ላይ ሰው ሲጨመር የሚቆጥር ---
@bot.message_handler(content_types=['new_chat_members'])
def count_adds(m):
    adder_id = m.from_user.id
    new_members_count = len(m.new_chat_members)
    if adder_id not in user_counts: user_counts[adder_id] = 0
    user_counts[adder_id] += new_members_count

# --- ለ. ግሩፕ ጠባቂ (50 ሰው ካልሞላ መልእክት ያጠፋል) ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def protect_group(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return 
    
    added_so_far = user_counts.get(uid, 0)
    if added_so_far < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ ግሩፑ ላይ ለመጻፍ መጀመሪያ 50 ሰው Add ማድረግ አለብህ።")
            threading.Timer(5, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

# --- ሐ. የጥገና ምዝገባ (በቅድመ ሁኔታ የታጀበ) ---
@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def check_and_start(m):
    uid = m.from_user.id
    
    # 🌟 አድሚን ከሆነ በቀጥታ ያልፋል
    if uid in ADMIN_IDS:
        user_registry[uid] = {}
        msg = bot.send_message(uid, "ሰላም ባለቤት! ምዝገባውን እንጀምር።\n\n📋 **ደረጃ 1/5**\nሙሉ ስም ያስገቡ?")
        bot.register_next_step_handler(msg, process_name)
        return

    # 🌟 ደንበኛ ከሆነ ቼክ ይደረጋል
    if uid in registered_users:
        bot.send_message(uid, "⚠️ ትዕዛዝዎ ለአቤል ቴክ ደርሷል! በቅርቡ እንደውልልዎታለን።")
        return

    added_so_far = user_counts.get(uid, 0)
    if added_so_far < 50:
        bot.send_message(uid, f"⚠️ **ቅድመ ሁኔታ!**\n\nጥገና ለመመዝገብ መጀመሪያ ግሩፑ ላይ 50 ሰው መጨመር አለብዎት።\n\nእስካሁን የጨመሩት፦ {added_so_far} ሰው\nየሚቀረዎት፦ {50 - added_so_far} ሰው")
        return

    # 50 ሰው የሞላ ደንበኛ
    user_registry[uid] = {}
    msg = bot.send_message(uid, "✅ ቅድመ ሁኔታውን ስላሟሉ እናመሰግናለን! ምዝገባውን እንጀምር።\n\n📋 **ደረጃ 1/5**\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    user_registry[uid]['name'] = m.text
    menu = "📋 **ደረጃ 2/5**\nየሚጠገነውን ዕቃ በቁጥር ይምረጡ፦\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(uid, menu)
    bot.register_next_step_handler(msg, process_item)

def process_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(uid, "📋 **ደረጃ 3/5**\nዕቃው የሚገኝበትን አድራሻ ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
    else:
        msg = bot.send_message(uid, "⚠️ እባክዎ ከ1-7 ያለውን ቁጥር ብቻ ይጠቀሙ።")
        bot.register_next_step_handler(msg, process_item)

def process_loc(m):
    uid = m.from_user.id
    user_registry[uid]['loc'] = m.text
    msg = bot.send_message(uid, "📋 **ደረጃ 4/5**\nስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    uid = m.from_user.id
    if m.text.isdigit() and len(m.text) >= 9:
        user_registry[uid]['phone'] = m.text
        msg = bot.send_message(uid, "📋 **ደረጃ 5/5**\nየዕቃውን ፎቶ ይላኩ?")
        bot.register_next_step_handler(msg, final)
    else:
        msg = bot.send_message(uid, "⚠️ ትክክለኛ ስልክ ያስገቡ።")
        bot.register_next_step_handler(msg, process_phone)

def final(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return
    
    # ደንበኛ ከሆነ ደግሞ እንዳይመዘገብ መቆለፍ
    if uid not in ADMIN_IDS: registered_users.add(uid)
    
    profile_link = f"tg://user?id={uid}"
    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n"
               f"👤 **ስም:** [{d['name']}]({profile_link})\n"
               f"🛠️ **ዕቃ:** {d['item']}\n"
               f"📍 **አድራሻ:** {d['loc']}\n"
               f"📞 **ስልክ:** `{d['phone']}`")
    
    # 🌟 ለባለቤቶቹ መላክ
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary, parse_mode="Markdown")
            else:
                bot.send_message(aid, summary, parse_mode="Markdown")
            print(f"✅ ለ Admin {aid} መልእክት ተልኳል")
        except Exception as e:
            print(f"❌ ለ Admin {aid} መላክ አልተቻለም: {e}")
    
    bot.send_message(uid, "✅ ተመዝግቧል! አቤል ቴክ፦ 0983664175\nቅርንጫፎች፦ አዲሱ ገበያ | አራብሳ | ሰሚት 72")
    user_registry.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    print("Abel Tech Bot is running...")
    bot.polling(non_stop=True)
