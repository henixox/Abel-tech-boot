import telebot
import os
from flask import Flask
from threading import Thread

# የቦት ቶከን
API_TOKEN = '8570487484:AAEnmwHvtg0cu-eaUyCSHoYA9sEr_5yzJtw'
bot = telebot.TeleBot(API_TOKEN)

app = Flask('')

@app.route('/')
def home():
    return "I am alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# /start ትእዛዝ ሲሰጥ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "እንኳን ወደ አቤል ቴክ (Abel Tech) በሰላም መጡ! 😊\n\n"
        "እኛ የቤት ውስጥ ዕቃዎችን በጥራት እንጠግናለን።\n"
        "ጥገና ለመመዝገብ መረጃዎን ይላኩልን።"
    )
    bot.reply_to(message, welcome_text)

# ማንኛውም ሌላ ጽሁፍ ሲላክ
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "መልእክትዎን ተቀብለናል! በቅርቡ በስልክ ቁጥርዎ እንደውላለን።")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    # ቦቱ ሁሌም ነቅቶ እንዲጠብቅ የሚያደርገው ዋናው መስመር
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
