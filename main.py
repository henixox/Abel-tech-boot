import telebot
from telebot import types
import re
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Abel Tech is Live!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- መቼቶች ---
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
ADMIN_IDS = [8596054746, 7443150824] 
bot = telebot.TeleBot(API_TOKEN)

ITEM_IMAGES = {
    "ፍሪጅ": "https://st2.depositphotos.com/1000128/7503/i/450/depositphotos_75039115-stock-photo-refrigerator-with-open-door.jpg",
    "ኦቭን": "http://googleusercontent.com/image_collection/image_retrieval/18292177481160207008_0",
    "ልብስ ማጠቢያ": "https://media.istockphoto.com/id/1144960519/photo/modern-washing-machine-in-laundry-room.jpg?s=612x612&w=0&k=20&c=L_qgI37FkH0_Y0QdE8H-j_f-vI6tHjGjK6rXpX9g-mI=",
    "ቴሌቪዥን": "https://t3.ftcdn.net/jpg/00/65/52/53/360_F_65525301_8uF0RzCgR6jHInOqE5K8oMUnqfO8K9mS.jpg",
    "ጀነሬተር": "http://googleusercontent.com/image_collection/image_retrieval/4900499586981707486_0",
    "AC": "http://googleusercontent.com/image_collection/image_retrieval/7819509568470222575_1",
    "Heat pump": "http://googleusercontent.com/image_collection/image_retrieval/17853399366638542416_0"
}

# --- ጅማሮ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = types.KeyboardButton('🛠️ ጥገና ለመመዝገብ')
    markup.add(btn)
    bot.send_message(message.chat.id, "እንኳን ወደ አቤል ቴክ በሰላም መጡ! 😊", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🛠️ ጥገና ለመመዝገብ')
def ask_name(message):
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 1/5**\n\nሙሉ ስምዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    name = message.text.strip()
    show_item_options(message, name)

def show_item_options(message, name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    items = list(ITEM_IMAGES.keys())
    for item in items:
        # እዚህ ጋር view: የሚል ኮድ ተጨምሯል
        markup.add(types.InlineKeyboardButton(item, callback_data=f"view:{item}:{name}"))
    bot.send_message(message.chat.id, f"📋 **ደረጃ 2/5**\n\n{name}፣ የሚጠገነውን ዕቃ ይምረጡ፦", reply_markup=markup)

# --- ⚠️ ይሄ ክፍል ነው መሽከርከሩን የሚያቆመው ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('view:'))
def view_item(call):
    # መሽከርከሩን ወዲያው ያቆመዋል
    bot.answer_callback_query(call.id)
    
    _, item, name = call.data.split(':')
    img_url = ITEM_IMAGES.get(item)
    
    markup = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton(f"✅ {item} ጥገና ይጀመር", callback_data=f"confirm:{item}:{name}")
    back_btn = types.InlineKeyboardButton("🔙 ተመለስ", callback_data=f"back:{name}")
    markup.add(confirm_btn, back_btn)

    caption = f"🔍 **የጥገና መረጃ፦ {item}**\n\nይህንን ዕቃ ለማስጠገን ከፈለጉ 'ጥገና ይጀመር' የሚለውን ይጫኑ።"
    
    # ምስሉን ይልካል
    bot.send_photo(call.message.chat.id, img_url, caption=caption, reply_markup=markup, parse_mode="Markdown")
    # የድሮውን ሜኑ ያጠፋዋል
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm:'))
def handle_confirm(call):
    bot.answer_callback_query(call.id)
    _, item, name = call.data.split(':')
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    msg = bot.send_message(call.message.chat.id, f"📋 **ደረጃ 3/5**\n\nየ {item} አድራሻ ይጻፉ?")
    bot.register_next_step_handler(msg, process_location, name, item)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back:'))
def handle_back(call):
    bot.answer_callback_query(call.id)
    name = call.data.split(':')[1]
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_item_options(call.message, name)

def process_location(message, name, item):
    location = message.text.strip()
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 4/5**\n\nስልክ ቁጥርዎን ያስገቡ?")
    bot.register_next_step_handler(msg, process_phone, name, item, location)

def process_phone(message, name, item, location):
    phone = message.text.strip()
    msg = bot.send_message(message.chat.id, "📋 **ደረጃ 5/5**\n\nየዕቃውን ፎቶ ይላኩ? (ፎቶ ከሌለ 'የለኝም' ይበሉ)")
    bot.register_next_step_handler(msg, final_step, name, item, location, phone)

def final_step(message, name, item, location, phone):
    summary = f"🚨 **አዲስ ትዕዛዝ**\n👤 ስም: {name}\n🛠️ ዕቃ: {item}\n📍 አድራሻ: {location}\n📞 ስልክ: `{phone}`"
    for admin_id in ADMIN_IDS:
        try:
            if message.content_type == 'photo':
                bot.send_photo(admin_id, message.photo[-1].file_id, caption=summary)
            else:
                bot.send_message(admin_id, summary + "\n🖼️ ፎቶ አልተላከም")
        except: pass
    bot.send_message(message.chat.id, "✅ **መረጃዎ ተመዝግቧል!** እናመሰግናለን! 😊")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=20)
