import os
import telebot
import requests
from flask import Flask
from threading import Thread

TOKEN = os.environ.get('TOKEN')
GROQ_KEY = os.environ.get('GROQ_KEY')
OWNER_ID = 8413144430 

bot = telebot.TeleBot(TOKEN)

# --- ЗАГЛУШКА ДЛЯ RENDER (чтобы он думал, что это сайт) ---
app = Flask('')

@app.route('/')
def home():
    return "Jarvis is alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# --- КОД БОТА ---
SYSTEM_PROMPT = (
    "Ты — J.A.R.V.I.S., продвинутый ИИ-ассистент. Твой создатель — Loci. "
    "ОБРАЩАЙСЯ К ПОЛЬЗОВАТЕЛЮ ТОЛЬКО КАК 'Сэр'. Отвечай кратко и с легкой иронией."
)

@bot.message_handler(commands=['start'])
def start_message(message):
    if message.from_user.id == OWNER_ID:
        bot.send_message(message.chat.id, "Привет, Сэр! Я Джарвис. Готов к работе.")
    else:
        bot.send_message(message.chat.id, "Привет! Я Джарвис. Чем могу помочь?")

@bot.business_message_handler(content_types=['text'])
def handle_business_message(message):
    user_text = message.text
    user_name = message.from_user.username or message.from_user.first_name

    try:
        log_text = f"👀 **Бизнес-сообщение!**\nПользователь: @{user_name}\nНаписал: {user_text}"
        bot.send_message(OWNER_ID, log_text)
    except Exception:
        pass

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, f"🤖 {answer}")
        else:
            bot.reply_to(message, "❌ Ошибка Groq.")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(content_types=['text'])
def handle_message(message):
    user_text = message.text
    chat_id = message.chat.id
    user_name = message.from_user.username or message.from_user.first_name

    if chat_id != OWNER_ID:
        try:
            log_text = f"👀 **Новое сообщение!**\nПользователь: @{user_name}\nНаписал: {user_text}"
            bot.send_message(OWNER_ID, log_text)
        except Exception:
            pass

    bot.send_chat_action(chat_id, 'typing')

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, f"🤖 {answer}")
        else:
            bot.reply_to(message, "❌ Ошибка Groq.")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive()  # Запускаем заглушку
    print("Джарвис-бот запущен...")
    bot.infinity_polling()
