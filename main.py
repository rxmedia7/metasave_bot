import os
from flask import Flask, request
import requests
from yt_dlp import YoutubeDL
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

app = Flask(__name__)

# Languages
LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский"
}

QUALITY_OPTIONS = ["144p", "240p", "360p", "480p", "720p", "1080p"]

# --- START MESSAGE HANDLER ---
def send_language_menu(chat_id):
    keyboard = [[InlineKeyboardButton(name, callback_data=f"lang:{code}")]
                for code, name in LANGUAGES.items()]
    bot.send_message(chat_id, "Choose language:", reply_markup=InlineKeyboardMarkup(keyboard))

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_language_menu(chat_id)

        elif "youtube.com" in text or "youtu.be" in text:
            keyboard = [[InlineKeyboardButton(q, callback_data=f"quality:{q}|{text}")]
                        for q in QUALITY_OPTIONS]
            bot.send_message(chat_id, "Choose quality:", reply_markup=InlineKeyboardMarkup(keyboard))

    if "callback_query" in data:
        cq = data["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        cid = cq["id"]
        data_c = cq["data"]

        bot.answer_callback_query(cid)

        # language select
        if data_c.startswith("lang:"):
            code = data_c.split(":")[1]
            bot.send_message(chat_id, f"Language set to: {LANGUAGES[code]}")

        # quality + download
        if data_c.startswith("quality:"):
            quality, url = data_c.replace("quality:", "").split("|")

            bot.send_message(chat_id, f"Downloading {quality}...")

            ydl_opts = {
                "format": f"best[height<={quality.replace('p','')}]",
                "outtmpl": "video.mp4"
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            bot.send_video(chat_id, video=open("video.mp4", "rb"))

    return "ok"