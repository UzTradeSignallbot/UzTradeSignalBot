import telebot
from telebot import types
import json
import os

BOT_TOKEN = '7915532190:AAGEA7Eb1LE4A7pUeWPZUNr7WNRk80Iv2qc'
bot = telebot.TeleBot(BOT_TOKEN)

users_data_file = 'users.json'
photo_path = 'signal_template.jpg'
caption = "💹 Signal: XAUUSD\n📈 Yo‘nalish: BUY\n🎯 TP: 2350.00\n🛑 SL: 2320.00"

# Foydalanuvchi bazasini yuklash
def load_users():
    if os.path.exists(users_data_file):
        with open(users_data_file, 'r') as file:
            return json.load(file)
    return {}

# Foydalanuvchini saqlash
def save_user(user_id, user_data):
    users = load_users()
    users[str(user_id)] = user_data
    with open(users_data_file, 'w') as file:
        json.dump(users, file)

# Start komandasi
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Foydalanuvchi"
    bot.send_message(user_id, f"👋 Salom, @{username}!\nBotga xush kelibsiz.")
    bot.send_message(user_id, "Iltimos, to‘liq ismingizni kiriting (F.I.O):")
    bot.register_next_step_handler(message, get_full_name)

# F.I.O
def get_full_name(message):
    full_name = message.text
    user_id = message.from_user.id
    save_user(user_id, {'full_name': full_name})
    bot.send_message(user_id, "Tug‘ilgan sanangizni kiriting (masalan: 01.01.2000):")
    bot.register_next_step_handler(message, get_birth_date)

# Tug‘ilgan sana
def get_birth_date(message):
    birth_date = message.text
    user_id = message.from_user.id
    user = load_users().get(str(user_id), {})
    user['birth_date'] = birth_date
    save_user(user_id, user)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)
    keyboard.add(button)
    bot.send_message(user_id, "Iltimos, telefon raqamingizni yuboring:", reply_markup=keyboard)

# Telefon
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    user_id = message.from_user.id
    contact = message.contact.phone_number
    user = load_users().get(str(user_id), {})
    user['phone'] = contact
    save_user(user_id, user)

    bot.send_message(user_id, "Endi selfi rasmingizni yuboring.", reply_markup=types.ReplyKeyboardRemove())

# Rasm qabul qilish
@bot.message_handler(content_types=['photo'])
def get_photo(message):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    user = load_users().get(str(user_id), {})
    user['photo'] = photo_id
    save_user(user_id, user)

    bot.send_message(user_id, "✅ Siz muvaffaqiyatli ro‘yxatdan o‘tdingiz.\nSignal olish uchun /signal buyrug‘ini bosing.")

# Signal komandasi
@bot.message_handler(commands=['signal'])
def send_signal(message):
    user_id = message.from_user.id
    user = load_users().get(str(user_id))
    if not user or not all(k in user for k in ['full_name', 'birth_date', 'phone', 'photo']):
        bot.send_message(user_id, "❌ Avval ro‘yxatdan o‘ting. /start buyrug‘ini bosing.")
        return

    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo:
            bot.send_photo(user_id, photo, caption=caption)
    else:
        bot.send_message(user_id, caption)

print("✅ Bot ishga tushdi...")
bot.infinity_polling()
