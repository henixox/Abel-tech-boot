import telebot
from telebot import types
import re
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

completed_users = set()
user_in_progress = {}

@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def group_protector(message):
    if re.search(r'http[s]?://', message.text or ""):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except: pass

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in completed_users:
        bot.send_message(message.chat.id, "🙏 **አቤል ቴክ፦** መረጃዎ ደርሶናል፣ በቅርቡ እንደውልልዎታለን።")
        return
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = types.KeyboardButton('🛠️ ጥገና ለመመዝገብ')
    markup.add(btn)
    bot.send_message(message.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(message):
    user_id = message.from_user.id
    if user_id in completed_users: return
    user_in_progress[user_id] = True
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    if not message.text or len(message.text.strip()) < 2:
        msg = bot.send_message(message.chat.id, "❌ ስም በትክክል ያስገቡ?")
        bot.register_next_step_handler(msg, process_name)
        return
    name = message.text.strip()
    show_item_options(message, name)

def show_item_options(message, name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    items = ["ፍሪጅ", "ኦቭን", "ልብስ ማጠቢያ", "ቴሌቪዥን", "ጀነሬተር", "AC", "Heat pump"]
    for item in items:
        markup.add(types.InlineKeyboardButton(item, callback_data=f"item:{item}:{name}:{message.from_user.id}"))
    bot.send_message(message.chat.id, f"📋 **ደረጃ 2/5**\n\n{name}፣ የሚጠገነውን ዕቃ ይምረጡ፦", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('item:'))
def handle_item_selection(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    _, item, name, user_id = call.data.split(':')
    msg = bot.send_message(call.message.chat.id, f"📋 **ደረጃ 3/5**\n\nየ {item} አድራሻ ይጻፉ?")
    bot.register_next_step_handler(msg, process_location, name, item, user_id)

def process_location(message, name, item, user_id):
    if not message.text or len(message.text.strip()) < 3:
        msg = bot.send_message(message.chat.id, "❌ አድራሻ በትክክል ይጻፉ?")
        bot.register_next_step_handler(msg, process_location, name, item, user_id)
        return
    location = message.text.strip()
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 4/5**\n\nስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone, name, item, location, user_id)

def process_phone(message, name, item, location, user_id):
    phone = message.text.strip()
    if not phone or not re.search(r'\d{9,}', phone):
        msg = bot.send_message(message.chat.id, "❌ ስልክ በትክክል ያስገቡ?")
        bot.register_next_step_handler(msg, process_phone, name, item, location, user_id)
        return
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 5/5**\n\nየዕቃውን ፎቶ ይላኩ? (ፎቶ ከሌለ 'የለኝም' ብለው ይጻፉ)")
    bot.register_next_step_handler(msg, final_step, name, item, location, user_id, phone)

def final_step(message, name, item, location, user_id, phone):
    tg_link = f"tg://user?id={user_id}"
    summary = f"🚨 **አዲስ ትዕዛዝ**\n\n👤 ስም: [{name}]({tg_link})\n🛠️ ዕቃ: {item}\n📍 አድራሻ: {location}\n📞 ስልክ: `{phone}`"
    for admin_id in ADMIN_IDS:
        try:
            if message.content_type == 'photo':
                bot.send_photo(admin_id, message.photo[-1].file_id, caption=summary, parse_mode="Markdown")
            else:
                bot.send_message(admin_id, summary + "\n🖼️ ፎቶ አልተላከም", parse_mode="Markdown")
        except: pass
    bot.send_message(message.chat.id, f"✅ **መረጃዎ ተመዝግቧል!**\n\nስም: {name}\nዕቃ: {item}\nስልክ: {phone}\n\nእናመሰግናለን! 😊")
    completed_users.add(int(user_id))
    user_in_progress.pop(int(user_id), None)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
