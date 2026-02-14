import telebot
from telebot import types
from flask import Flask
from threading import Thread

# 1. ሰርቨር እንዳይዘጋ
app = Flask('')
@app.route('/')
def home(): return "Abel Tech Speed Version!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# 2. መቼቶች
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824]
bot = telebot.TeleBot(API_TOKEN)
user_data = {}

# አጫጭር የምስል ሊንኮች
IMG = {
    "ፍሪጅ": "https://tinyurl.com/fridge-rep",
    "ኦቭን": "https://tinyurl.com/oven-rep",
    "ልብስ ማጠቢያ": "https://tinyurl.com/wash-rep",
    "ቴሌቪዥን": "https://tinyurl.com/tv-rep",
    "ጀነሬተር": "https://tinyurl.com/gen-rep",
    "AC": "https://tinyurl.com/ac-rep"
}

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('🛠️ ጥገና ለመመዝገብ')
    bot.send_message(m.chat.id, "እንኳን ወደ አቤል ቴክ መጡ! 😊", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(m):
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 1/5**\nስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(m):
    user_data[m.from_user.id] = {'name': m.text}
    kb = types.InlineKeyboardMarkup(row_width=2)
    # እዚህ ጋር ዳታውን አሳጥሬዋለሁ 's:' ማለት Select ማለት ነው
    btns = [types.InlineKeyboardButton(i, callback_data=f"s:{i}") for i in IMG]
    kb.add(*btns)
    bot.send_message(m.chat.id, "📋 **ደረጃ 2/5**\nየሚጠገነውን ዕቃ ይምረጡ፦", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: True)
def fast_call(c):
    # መሽከርከሩን ወዲያውኑ ለማቆም
    bot.answer_callback_query(c.id)
    uid = c.from_user.id
    
    if c.data.startswith('s:'):
        item = c.data.split(':')[1]
        user_data[uid]['item'] = item
        
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(f"✅ የ{item} ጥገና ይጀመር", callback_data="go"))
        kb.add(types.InlineKeyboardButton("🔙 ተመለስ", callback_data="back"))
        
        # ምስሉን እዚህ ጋር ይልካል
        bot.send_photo(c.message.chat.id, IMG.get(item), caption=f"🔍 {item} ተመርጧል። ይጀመር?", reply_markup=kb)
        bot.delete_message(c.message.chat.id, c.message.message_id)
        
    elif c.data == "go":
        item = user_data[uid]['item']
        bot.delete_message(c.message.chat.id, c.message.message_id)
        msg = bot.send_message(c.message.chat.id, f"📋 **ደረጃ 3/5**\nየ {item} አድራሻ ይጻፉ?")
        bot.register_next_step_handler(msg, process_loc)
        
    elif c.data == "back":
        bot.delete_message(c.message.chat.id, c.message.message_id)
        process_name(c.message)

def process_loc(m):
    user_data[m.from_user.id]['loc'] = m.text
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 4/5**\nስልክ ቁጥር ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone)

def process_phone(m):
    user_data[m.from_user.id]['phone'] = m.text
    msg = bot.send_message(m.chat.id, "📋 **ደረጃ 5/5**\nፎቶ ይላኩ (ወይም 'የለኝም' ይበሉ)?")
    bot.register_next_step_handler(msg, final)

def final(m):
    uid = m.from_user.id
    d = user_data.get(uid)
    if not d: return
    
    link = f"tg://user?id={uid}"
    res = f"🚨 **አዲስ ትዕዛዝ**\n👤 **ስም:** [{d['name']}]({link})\n🛠️ **ዕቃ:** {d['item']}\n📍 **አድራሻ:** {d['loc']}\n📞 **ስልክ:** `{d['phone']}`"
    
    for aid in ADMIN_IDS:
        try:
            if m.content_type == 'photo': bot.send_photo(aid, m.photo[-1].file_id, caption=res, parse_mode="Markdown")
            else: bot.send_message(aid, res + "\n🖼️ ፎቶ የለም", parse_mode="Markdown")
        except: pass
        
    bot.send_message(m.chat.id, "✅ ጥያቄዎ ለአቤል ቴክ ደርሷል። በቅርቡ እንደውልልዎታለን።")
    user_data.pop(uid, None)

if __name__ == "__main__":
    keep_alive()
    bot.polling(non_stop=True)
