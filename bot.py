import telebot
from telebot import types
import re
import os

TOKEN = '7915532190:AAGEA7Eb1LE4A7pUeWPZUNr7WNRk80Iv2qc'
ADMIN_USERNAME = '@JumaboyIsmoilov'
BOT_USERNAME = '@UzTradeSignallBot'
ADMIN_ID = 7224380835

bot = telebot.TeleBot(TOKEN)
users = {}

def valid_fio(text):
    return len(text.split()) >= 2 and all(part.isalpha() for part in text.split())

def valid_birthdate(text):
    return bool(re.match(r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-[0-9]{4}$", text))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in users:
        bot.send_message(user_id, "👋 Siz allaqachon ro'yxatdan o'tgansiz.")
        return

    bot.send_sticker(user_id, 'CAACAgIAAxkBAAEFv4lfZRL_8cTCWB0mjRZgBFG-k5A2sgAC1yEAAoHBTUoMAAFzK0XATIQE')
    bot.send_message(user_id, f"👋 Assalomu alaykum, {message.from_user.first_name}!")
    bot.send_message(user_id, f"👤 Iltimos, to'liq ism-sharifingizni kiriting:")
    bot.register_next_step_handler(message, process_fio)

def process_fio(message):
    if not valid_fio(message.text):
        bot.send_message(message.chat.id, "❌ Siz xato kiritdingiz. Iltimos, F.I.O.ni to'g'ri yozing (masalan: Islom Karimov).")
        bot.register_next_step_handler(message, process_fio)
        return

    users[message.from_user.id] = {'fio': message.text}
    bot.send_message(message.chat.id, "📅 Tug'ilgan kuningizni kiriting (DD-MM-YYYY):")
    bot.register_next_step_handler(message, process_birthdate)

def process_birthdate(message):
    if not valid_birthdate(message.text):
        bot.send_message(message.chat.id, "❌ Tug'ilgan sana noto'g'ri formatda. DD-MM-YYYY shaklida kiriting.")
        bot.register_next_step_handler(message, process_birthdate)
        return

    users[message.from_user.id]['birthdate'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton(text="📞 Raqamni yuborish", request_contact=True)
    markup.add(contact_btn)
    bot.send_message(message.chat.id, "📞 Telefon raqamingizni yuboring:", reply_markup=markup)
    bot.register_next_step_handler(message, process_contact)

def process_contact(message):
    if not message.contact:
        bot.send_message(message.chat.id, "❌ Iltimos, tugmani bosib raqamingizni yuboring.")
        bot.register_next_step_handler(message, process_contact)
        return

    users[message.from_user.id]['phone'] = message.contact.phone_number
    bot.send_message(message.chat.id, "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=types.ReplyKeyboardRemove())
    send_main_menu(message.chat.id)

def send_main_menu(user_id):
    markup = types.InlineKeyboardMarkup()
    admin_btn = types.InlineKeyboardButton("👨‍💼 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME[1:]}")
    markup.add(admin_btn)
    bot.send_message(user_id, "🏠 Asosiy menyu:", reply_markup=markup)

@bot.message_handler(commands=['signal'])
def send_signal(message):
    if message.from_user.id != ADMIN_ID:
        return

    caption = (
        "📊 Signal: XAUUSD\n"
        "🕒 Vaqt: 20:59\n"
        "📈 Yo'nalish: BUY\n"
        "💰 Narx: 2352.15\n"
        "📉 SL: 2345.00\n"
        "📊 TP: 2370.00\n"
        "✅ Kafolat: 100%\n\n"
        f"📩 @{BOT_USERNAME[1:]}"
    )
    photo_path = 'signal_template.jpg'
    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            for user_id in users:
                bot.send_photo(user_id, photo, caption=caption)
    else:
        for user_id in users:
            bot.send_message(user_id, caption)

bot.infinity_polling()