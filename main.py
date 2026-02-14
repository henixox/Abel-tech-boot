import telebot
from telebot import types
import re
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Abel Tech Security is Active!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

completed_users = set()

# 🛡️ ዋናው የሊንክ መከላከያ (በግልም በግሩፕም ይሰራል)
@bot.message_handler(func=lambda message: re.search(r'(http://|https://|www\.|t\.me/|bit\.ly/)', (message.text or "").lower()))
def link_protector(message):
    try:
        # መጀመሪያ ሊንኩን ይሰርዘዋል
        bot.delete_message(message.chat.id, message.message_id)
        # ማስጠንቀቂያ ይሰጣል
        bot.send_message(message.chat.id, "❌ **ሊንክ መላክ የተከለከለ ነው!**")
    except:
        # ቦቱ አድሚን ካልሆነና መሰረዝ ካልቻለ ሪፕላይ ያደርጋል
        bot.reply_to(message, "❌ ሊንክ መላክ አይፈቀድም!")

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in completed_users:
        bot.send_message(message.chat.id, "🙏 **አቤል ቴክ፦** መረጃዎ ደርሶናል፣ በቅርቡ እንደውልልዎታለን።")
        return
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = types.KeyboardButton('🛠️ ጥገና ለመመዝገብ')
    markup.add(btn)
    bot.send_message(message.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(message):
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    # ስም ቦታ ላይ ሊንክ ቢላክ ለመከላከል
    if re.search(r'(http|https|www\.|t\.me)', (message.text or "").lower()):
        msg = bot.send_message(message.chat.id, "❌ ሊንክ አይፈቀድም! እባክዎ ስምዎን ብቻ ያስገቡ?")
        bot.register_next_step_handler(msg, process_name)
        return
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
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    _, item, name, user_id = call.data.split(':')
    msg = bot.send_message(call.message.chat.id, f"📋 **ደረጃ 3/5**\n\nየ {item} አድራሻ ይጻፉ?")
    bot.register_next_step_handler(msg, process_location, name, item, user_id)

def process_location(message, name, item, user_id):
    if re.search(r'(http|https|www\.|t\.me)', (message.text or "").lower()):
        msg = bot.send_message(message.chat.id, "❌ ሊንክ አይፈቀድም! አድራሻዎን ብቻ ይጻፉ?")
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
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 5/5**\n\nየዕቃውን ፎቶ ይላኩ? (ፎቶ ከሌለ 'የለኝም' ይበሉ)")
    bot.register_next_step_handler(msg, final_step, name, item, location, user_id, phone)

def final_step(message, name, item, location, user_id, phone):
    summary = f"🚨 **አዲስ ትዕዛዝ**\n👤 ስም: {name}\n🛠️ ዕቃ: {item}\n📍 አድራሻ: {location}\n📞 ስልክ: `{phone}`"
    for admin_id in ADMIN_IDS:
        try:
            if message.content_type == 'photo':
                bot.send_photo(admin_id, message.photo[-1].file_id, caption=summary)
            else:
                bot.send_message(admin_id, summary + "\n🖼️ ፎቶ አልተላከም")
        except: pass
    bot.send_message(message.chat.id, "✅ **መረጃዎ ተመዝግቧል!** እናመሰግናለን! 😊")
    completed_users.add(int(user_id))

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=20)
