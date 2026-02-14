import telebot
from telebot import types
from flask import Flask
from threading import Thread
import threading

# 1. ሰርቨር እንዳይዘጋ
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Strict System is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

# ዳታቤዝ (በሜሞሪ ላይ)
user_counts = {}       # አድ ያደረጉት ሰዎች ብዛት
registered_users = set() # ምዝገባ የጨረሱ ሰዎች ዝርዝር (ለመቆለፍ)
user_registry = {}      # ለምዝገባ ሂደት ጊዜያዊ መያዣ

ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. ግሩፕ ላይ ሰው ሲጨመር የሚቆጥር ---
@bot.message_handler(content_types=['new_chat_members'])
def count_adds(m):
    adder_id = m.from_user.id
    new_members_count = len(m.new_chat_members)
    if adder_id not in user_counts: user_counts[adder_id] = 0
    user_counts[adder_id] += new_members_count

# --- ለ. ግሩፕ ጠባቂ (50 ሰው ካልሞላ አይጻፍም) ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def protect_group(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return 
    
    added_so_far = user_counts.get(uid, 0)
    if added_so_far < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            needed = 50 - added_so_far
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ ግሩፑ ላይ ለመጻፍ ግዴታ 50 ሰው Add ማድረግ አለብህ። (የቀረህ፦ {needed} ሰው)")
            threading.Timer(7, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

# --- ሐ. የጥገና ምዝገባ (በቦቱ Inbox) ---
@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ' and m.chat.type == 'private')
def start_registration(m):
    uid = m.from_user.id
    
    # 🌟 1ኛ መቆለፊያ፦ አንዴ መመዝገቡን ቼክ ያደርጋል
    if uid in registered_users:
        bot.send_message(m.chat.id, "⚠️ **ትዕዛዝዎ ቀድሞውኑ ለአቤል ቴክ ደርሷል!**\n\nበቅርቡ በስልክ እንገናኝዎታለን። ደጋግሞ መመዝገብ አያስፈልግም። እናመሰግናለን! 🙏")
        return

    # 🌟 2ኛ መቆለፊያ፦ 50 ሰው መሙላቱን ቼክ ያደርጋል
    added_so_far = user_counts.get(uid, 0)
    if added_so_far < 50:
        bot.send_message(m.chat.id, f"⚠️ ይቅርታ፣ ጥገና ለመመዝገብ መጀመሪያ ግሩፑ ላይ 50 ሰው መጨመር አለብዎት።\n\nእስካሁን የጨመሩት፦ {added_so_far} ሰው ብቻ ነው።")
        return

    user_registry[uid] = {}
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    user_registry[uid]['name'] = m.text.strip()
    menu = "📋 **ደረጃ 2/5**\n\nዕቃ በቁጥር ይምረጡ፦\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(m.chat.id, menu)
    bot.register_next_step_handler(msg, process_item)

def process_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(m.chat.id, "📋 **ደረጃ 3/5**\nአድራሻ ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
    else:
        msg = bot.send_message(m.chat.id, "⚠️ ከ 1-7 ቁጥር ይጠቀሙ።")
        bot.register_next_step_handler(msg, process_item)

def process_loc(m):
    uid = m.from_user.id
    user_registry[uid]['loc'] = m.text.strip()
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 4/5**\nስልክ ቁጥር ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    uid = m.from_user.id
    phone = m.text.strip()
    if phone.isdigit() and len(phone) >= 9:
        user_registry[uid]['phone'] = phone
        msg = bot.send_message(m.chat.id, "📋 **ደረጃ 5/5**\nየዕቃውን ፎቶ እዚህ ይላኩ?")
        bot.register_next_step_handler(msg, final)
    else:
        msg = bot.send_message(m.chat.id, "⚠️ ትክክለኛ ስልክ ቁጥር ያስገቡ።")
        bot.register_next_step_handler(msg, process_phone)

def final(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return
    
    # ምዝገባው መጠናቀቁን በቋሚነት መመዝገብ
    registered_users.add(uid)
    
    profile_link = f"tg://user?id={uid}"
    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n"
               f"👤 **ስም:** [{d['name']}]({profile_link})\n"
               f"🛠️ **ዕቃ:** {d['item']}\n"
               f"📍 **አድራሻ:** {d['loc']}\n"
               f"📞 **ስልክ:** `{d['phone']}`")
    
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary, parse_mode="Markdown")
            else:
                bot.send_message(aid, summary, parse_mode="Markdown")
        except: pass
    
    bot.send_message(m.chat.id, "✅ **ጥያቄዎ ለአቤል ቴክ ደርሷል!**\n\nስልክ፦ 0983664175 (Abel)\nአድራሻ፦ አዲሱ ገበያ | አራብሳ | ሰሚት 72")
    user_registry.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
