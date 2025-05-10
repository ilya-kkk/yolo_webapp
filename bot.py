from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    keyboard = [[
        InlineKeyboardButton("🚀 Открыть WebApp", web_app=WebAppInfo(url="https://abcd1234.ngrok.io/web"))
    ]]
    update.message.reply_text("Нажми кнопку ниже:", reply_markup=InlineKeyboardMarkup(keyboard))
