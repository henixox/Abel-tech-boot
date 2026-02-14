import telebot
from telebot import types
import threading

# 1. መሠረታዊ መቼቶች (Settings)
# @BotFather ላይ የሰጠህን Token እዚህ ጋር በትክክል አስገባ
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'

# የአንተ እና የአቤል ID - እነዚህ ሰዎች 50 ሰው ሳይጨምሩ መጻፍ ይችላሉ
ADMIN_IDS = [8596054746, 7443150824] 

bot = telebot.TeleBot(API_TOKEN)

# ጊዜያዊ ዳታ ማስቀመጫ
user_counts = {}  # ሰዎች ስንት ሰው እንደጨመሩ ለመቁጠር
user_registry = {} # ለጥገና ምዝገባ መረጃ መያዣ

# የሚጠገኑ ዕቃዎች ዝርዝር
ITEMS = {"1": "ፍሪጅ", "2": "ኦቭን", "3": "ልብስ ማጠቢያ", "4": "ቴሌቪዥን", "5": "ጀነሬተር", "6": "AC", "7": "Heat pump"}

# --- ሀ. ግሩፑን የሚጠብቅ ክፍል (50 ሰው ካልሞላ ያጠፋል) ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def protect_group(m):
    uid = m.from_user.id
    
    # አድሚን ከሆነ ወይም አንተ ከሆንክ ዝለለው
    if uid in ADMIN_IDS:
        return 
    
    # የጨመረውን ሰው ብዛት ቼክ አድርግ
    added_so_far = user_counts.get(uid, 0)
    
    if added_so_far < 50:
        try:
            # መልእክቱን አጥፋ
            bot.delete_message(m.chat.id, m.message_id)
            
            # ማስጠንቀቂያ ላክና ከ5 ሰከንድ በኋላ መልሰህ አጥፋው
            warn = bot.send_message(m.chat.id, f"⚠️ {m.from_user.first_name}፣ ግሩፑ ላይ ለመጻፍ መጀመሪያ 50 ሰው Add ማድረግ አለብህ። (እስካሁን ያደረግከው: {added_so_far})")
            threading.Timer(5, lambda: bot.delete_message(m.chat.id, warn.message_id)).start()
        except Exception as e:
            print(f"Error in deleting: {e}")

# --- ለ. ሰው ሲጨመር የሚቆጥር ክፍል ---
@bot.message_handler(content_types=['new_chat_members'])
def count_adds(m):
    adder_id = m.from_user.id
    new_members = len(m.new_chat_members)
    
    if adder_id not in user_counts:
        user_counts[adder_id] = 0
    
    user_counts[adder_id] += new_members
    print(f"User {adder_id} added {new_members} members. Total: {user_counts[adder_id]}")

# --- ሐ. የጥገና ምዝገባ (Private Chat ላይ ብቻ) ---
@bot.message_handler(commands=['start'])
def start_cmd(m):
    if m.chat.type == 'private':
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add('🛠️ ጥገና ለመመዝገብ')
        bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ መጡ! ጥገና ለመመዝገብ ከታች ያለውን ይጫኑ።", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def check_requirements(m):
    uid = m.from_user.id
    
    # አድሚን ከሆነ በቀጥታ ያልፋል፣ ደንበኛ ከሆነ 50 ሰው መጨመሩ ይረጋገጣል
    added = user_counts.get(uid, 0)
    if uid in ADMIN_IDS or added >= 50:
        user_registry[uid] = {}
        msg = bot.send_message(uid, "✅ ምዝገባ እንጀምር። ሙሉ ስምዎን ያስገቡ?")
        bot.register_next_step_handler(msg, get_name)
    else:
        bot.send_message(uid, f"⚠️ ይቆዩ! ጥገና ለመመዝገብ መጀመሪያ ግሩፑ ላይ 50 ሰው መጨመር አለብዎት።\nእስካሁን የጨመሩት: {added}")

def get_name(m):
    uid = m.from_user.id
    user_registry[uid]['name'] = m.text
    menu = "የሚጠገነውን ዕቃ በቁጥር ይምረጡ:\n"
    for k, v in ITEMS.items(): menu += f"{k}. {v}\n"
    msg = bot.send_message(uid, menu)
    bot.register_next_step_handler(msg, get_item)

def get_item(m):
    uid = m.from_user.id
    if m.text in ITEMS:
        user_registry[uid]['item'] = ITEMS[m.text]
        msg = bot.send_message(uid, "አድራሻዎን ይጻፉ?")
        bot.register_next_step_handler(msg, get_loc)
    else:
        bot.send_message(uid, "እባክዎ ከ1-7 ያለውን ቁጥር ብቻ ይጠቀሙ።")
        bot.register_next_step_handler(m, get_item)

def get_loc(m):
    uid = m.from_user.id
    user_registry[uid]['loc'] = m.text
    msg = bot.send_message(uid, "ስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(m):
    uid = m.from_user.id
    user_registry[uid]['phone'] = m.text
    msg = bot.send_message(uid, "የዕቃውን ፎቶ ይላኩ?")
    bot.register_next_step_handler(msg, finish_registration)

def finish_registration(m):
    uid = m.from_user.id
    d = user_registry.get(uid)
    if not d: return

    summary = (f"🚨 **አዲስ ትዕዛዝ**\n\n"
               f"👤 ስም: {d['name']}\n"
               f"🛠️ ዕቃ: {d['item']}\n"
               f"📍 አድራሻ: {d['loc']}\n"
               f"📞 ስልክ: {d['phone']}")

    # ለአድሚኖች Inbox መላክ
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo':
                bot.send_photo(aid, m.photo[-1].file_id, caption=summary)
            else:
                bot.send_message(aid, summary)
        except: pass

    bot.send_message(uid, "✅ ምዝገባዎ ተጠናቋል። በቅርቡ እንደውልልዎታለን!")
    user_registry.pop(uid, None)

# ቦቱን ማስነሳት
print("Abel Tech Bot is Online...")
bot.infinity_polling()
