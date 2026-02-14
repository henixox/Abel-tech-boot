import telebot
from telebot import types
import threading

API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

user_counts = {}
user_registry = {}
ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ግሩፑን የሚጠብቅ ክፍል ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def protect_group(m):
    uid = m.from_user.id
    if uid in ADMIN_IDS: return 
    added = user_counts.get(uid, 0)
    if added < 50:
        try:
            bot.delete_message(m.chat.id, m.message_id)
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ መጀመሪያ 50 ሰው Add ያድርጉ (ያደረጉት: {added})")
            threading.Timer(5, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except: pass

@bot.message_handler(content_types=['new_chat_members'])
def count_adds(m):
    adder_id = m.from_user.id
    user_counts[adder_id] = user_counts.get(adder_id, 0) + len(m.new_chat_members)

# --- ምዝገባ ክፍል ---
@bot.message_handler(commands=['start'])
def start_cmd(m):
    if m.chat.type == 'private':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "ሰላም! የአቤል ቴክ ጥገና መመዝገቢያ ቦት ነው።\n\n⚠️ ማሳሰቢያ፡ ጥገና ለመመዝገብ መጀመሪያ ግሩፑ ላይ 50 ሰው መጨመር አለብዎት።", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def init_reg(m):
    uid = m.from_user.id
    added = user_counts.get(uid, 0)
    
    # አንድ ሰው ገና ምዝገባ ላይ ከሆነ ደግሞ እንዳይመዘገብ
    if uid in user_registry and 'step' in user_registry[uid]:
        bot.send_message(uid, "⚠️ ምዝገባ እየካሄደ ነው። እባክዎ የቀረቡትን ጥያቄዎች ይመልሱ።")
        return

    # 50 ሰው መሙላቱን ቼክ ያደርጋል
    if uid in ADMIN_IDS or added >= 50:
        user_registry[uid] = {'step': 'name'} # ምዝገባ ጀመረ
        msg = bot.send_message(uid, "✅ 50 ሰው ስለሞሉ ምዝገባ መጀመር ይችላሉ። ሙሉ ስምዎን ያስገቡ?")
        bot.register_next_step_handler(msg, get_name)
    else:
        bot.send_message(uid, f"❌ ይቆዩ! ጥገና ለመመዝገብ መጀመሪያ ግሩፑ ላይ 50 ሰው መጨመር አለብዎት።\n\n📊 እስካሁን የጨመሩት፡ {added} ሰው\n📉 የቀረዎት፡ {50 - added} ሰው")

def get_name(m):
    uid = m.from_user.id
    if m.text == '🛠️ ጥገና ለመመዝገብ': return # በተኑን በስህተት ቢነካው እንዳይበላሽ
    user_registry[uid]['name'] = m.text
    user_registry[uid]['username'] = m.from_user.username
    user_registry[uid]['step'] = 'item'
    
    menu = "የሚጠገነውን ዕቃ በቁጥር ይምረጡ:\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(uid, menu)
    bot.register_next_step_handler(msg, get_item)

def get_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        user_registry[uid]['step'] = 'loc'
        msg = bot.send_message(uid, "አድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, get_loc)
    else:
        msg = bot.send_message(uid, "እባክዎ ከላይ ካሉት ቁጥሮች (1-7) አንዱን ይምረጡ።")
        bot.register_next_step_handler(msg, get_item)

def get_loc(m):
    uid = m.from_user.id
    user_registry[uid]['loc'] = m.text
    user_registry[uid]['step'] = 'phone'
    msg = bot.send_message(uid, "ስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(m):
    uid = m.from_user.id
    if m.text.isdigit() and len(m.text) >= 10:
        user_registry[uid]['phone'] = m.text
        user_registry[uid]['step'] = 'photo'
        msg = bot.send_message(uid, "የዕቃውን ፎቶ ይላኩ?")
        bot.register_next_step_handler(msg, finish_reg)
    else:
        msg = bot.send_message(uid, "❌ ስህተት፡ እባክዎ ትክክለኛ ስልክ ቁጥር ያስገቡ።")
        bot.register_next_step_handler(msg, get_phone)

def finish_reg(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return

    link = f"https://t.me/{d['username']}" if d['username'] else f"tg://user?id={uid}"
    
    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n"
               f"👤 ስም: [{d['name']}]({link})\n"
               f"🛠️ ዕቃ: {d['item']}\n"
               f"📍 አድራሻ: {d['loc']}\n"
               f"📞 ስልክ: `{d['phone']}`")

    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary, parse_mode='Markdown')
            else:
                bot.send_message(aid, summary, parse_mode='Markdown')
        except: pass

    bot.send_message(uid, "✅ ምዝገባዎ ተጠናቋል። በቅርቡ እንደውልልዎታለን!")
    user_registry.pop(uid, None) # ምዝገባውን ሙሉ በሙሉ ይዘጋል

print("Abel Tech Bot - Fixed Version is Running...")
bot.infinity_polling()
