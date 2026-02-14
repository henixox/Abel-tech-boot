import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. ሰርቨር እንዳይዘጋ (Keep-Alive)
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Bot is Fully Optimized!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

# የተጠቃሚዎች ዳታ መያዣ
user_registry = {}

ITEMS = {
    "1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", 
    "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('🛠️ ጥገና ለመመዝገብ')
    bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(m):
    uid = m.from_user.id
    user_registry[uid] = {} # አዲስ መዝገብ መክፈት
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    user_registry[uid]['name'] = m.text.strip()
    
    menu = "📋 **ደረጃ 2/5**\n\nየሚጠገነውን ዕቃ በቁጥር ይምረጡ፦\n\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(m.chat.id, menu)
    bot.register_next_step_handler(msg, process_item)

def process_item(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(m.chat.id, f"✅ {ITEMS[m.text]} ተመርጧል።\n\n📋 **ደረጃ 3/5**\n\nዕቃው የሚገኝበትን አድራሻ ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
    else:
        msg = bot.send_message(m.chat.id, "⚠️ እባክዎ ከ 1 እስከ 7 ያለውን ቁጥር ብቻ ይጠቀሙ?")
        bot.register_next_step_handler(msg, process_item)

def process_loc(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    user_registry[uid]['loc'] = m.text.strip()
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 4/5**\n\nትክክለኛ ስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    uid = m.from_user.id
    if uid not in user_registry: return
    phone_input = m.text.strip()
    
    # ስልክ ቁጥር ማጣሪያ
    if phone_input.isdigit() or (phone_input.startswith('+') and phone_input[1:].isdigit()):
        user_registry[uid]['phone'] = phone_input
        msg = bot.send_message(m.chat.id, "📋 **ደረጃ 5/5**\n\nየዕቃውን ፎቶ ይላኩ? (ፎቶ ከሌለ 'የለኝም' ብለው ይጻፉ)")
        bot.register_next_step_handler(msg, final)
    else:
        msg = bot.send_message(m.chat.id, "⚠️ ስህተት! እባክዎ ስልክ ቁጥርዎን በቁጥር ብቻ ያስገቡ?")
        bot.register_next_step_handler(msg, process_phone)

def final(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return
    
    profile_link = f"tg://user?id={uid}"
    summary = (f"🚨 **አዲስ ትዕዛዝ ደርሷል!**\n\n"
               f"👤 **ስም:** [{d['name']}]({profile_link})\n"
               f"🛠️ **ዕቃ:** {d['item']}\n"
               f"📍 **አድራሻ:** {d['loc']}\n"
               f"📞 **ስልክ:** `{d['phone']}`\n\n"
               f"👆 *ስሙን በመንካት ፕሮፋይሉን ማግኘት ይችላሉ።*")
    
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary, parse_mode="Markdown")
            else:
                bot.send_message(aid, summary, parse_mode="Markdown")
        except: pass
    
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
    
    # ዳታውን ማጽዳት
    user_registry.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
