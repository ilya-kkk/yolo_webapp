import os
import logging
import shutil
import numpy as np
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ultralytics import YOLO
from PIL import Image
import io

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загрузка модели YOLO
model = YOLO("yolov8n.pt")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Отправь мне фотографию, и я обработаю её с помощью YOLO."
    )

async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /memory"""
    try:
        # Получаем информацию о диске
        total, used, free = shutil.disk_usage("/")
        
        # Конвертируем в гигабайты
        total_gb = total // (2**30)
        used_gb = used // (2**30)
        free_gb = free // (2**30)
        
        # Формируем сообщение
        message = (
            "📊 Информация о диске:\n\n"
            f"Всего места: {total_gb} GB\n"
            f"Использовано: {used_gb} GB\n"
            f"Свободно: {free_gb} GB\n"
            f"Использовано: {used * 100 / total:.1f}%"
        )
        
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Ошибка при получении информации о диске: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при получении информации о диске."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text("иди нахуй")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий"""
    try:
        # Получаем фото
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()
        
        # Конвертируем в PIL Image
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Обрабатываем изображение с помощью YOLO
        results = model.predict(image, save=False)
        annotated_image = results[0].plot()
        
        # Исправляем цвета (BGR -> RGB)
        annotated_image = annotated_image[..., ::-1]
        
        # Конвертируем обратно в байты
        output = io.BytesIO()
        Image.fromarray(annotated_image).save(output, format='JPEG')
        output.seek(0)
        
        # Отправляем обработанное изображение
        await update.message.reply_photo(
            photo=output,
            caption="Вот обработанное изображение с обнаруженными объектами!"
        )
        
    except Exception as e:
        logging.error(f"Ошибка при обработке фото: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке фотографии."
        )

def main():
    """Запуск бота"""
    # Получаем токен из переменных окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения")

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("memory", memory))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
