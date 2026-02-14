import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. ሰርቨር እንዳይዘጋ
app = Flask('')
@app.route('/')
def home(): return "Abel Tech with Address is Live!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)
user_data = {}

ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('🛠️ ጥገና ለመመዝገብ')
    bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(m):
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(m):
    user_data[m.from_user.id] = {'name': m.text.strip()}
    menu = "📋 **ደረጃ 2/5**\n\nየሚጠገነውን ዕቃ በቁጥር ይምረጡ፦\n\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(m.chat.id, menu)
    bot.register_next_step_handler(msg, process_item)

def process_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_data[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(m.chat.id, f"✅ {ITEMS[m.text]} ተመርጧል።\n\n📋 **ደረጃ 3/5**\nአድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
    else:
        msg = bot.send_message(m.chat.id, "⚠️ እባክዎ ቁጥር (1-7) ብቻ ያስገቡ?")
        bot.register_next_step_handler(msg, process_item)

def process_loc(m):
    user_data[m.from_user.id]['loc'] = m.text.strip()
    msg = bot.send_message(m.chat.id, "📋 **ደراحة 4/5**\nስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    user_data[m.from_user.id]['phone'] = m.text.strip()
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 5/5**\nየዕቃውን ፎቶ ይላኩ? (ወይም 'የለኝም' ይበሉ)")
    bot.register_next_step_handler(msg, final)

def final(m):
    uid = m.from_user.id
    d = user_data.get(uid)
    if not d: return
    
    # ለአድሚን የሚላክ መረጃ
    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n👤 ስም: {d['name']}\n🛠️ ዕቃ: {d['item']}\n📍 አድራሻ: {d['loc']}\n📞 ስልክ: {d['phone']}\n🔗 ፕሮፋይል: tg://user?id={uid}")
    
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary)
            else:
                bot.send_message(aid, summary)
        except: pass
    
    # ለደንበኛው የሚላክ የአቤል ቴክ አድራሻ
    address_text = (
        "✅ **ጥያቄዎ ለአቤል ቴክ ደርሷል!**\n\n"
        "በቅርቡ በስልክ እንገናኝዎታለን። እስከዚያ ድረስ በነዚህ አድራሻዎቻችን ሊያገኙን ይችላሉ፦\n\n"
        "📞 **ስልክ:** 0983664175\n"
        "📍 **አድራሻዎቻችን፦**\n"
        "1. አዲሱ ገበያ\n"
        "2. አራብሳ ታንከር\n"
        "3. ሰሚት 72\n\n"
        "ስለመረጡን እናመሰግናለን! 😊"
    )
    bot.send_message(m.chat.id, address_text, parse_mode="Markdown")
    user_data.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
