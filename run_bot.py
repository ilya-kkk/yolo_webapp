import os
from telegram.ext import Updater, CommandHandler
from bot import start

# Получаем токен из переменной окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")

def main():
    # Инициализируем бота
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Добавляем обработчик команды /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 