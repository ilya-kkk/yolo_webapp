import os
import logging
import shutil
import numpy as np
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ultralytics import YOLO
from PIL import Image
import io
from openai import OpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Словарь с названиями классов
CLASS_NAMES = {
    0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus',
    6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant',
    11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat',
    16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear',
    22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag',
    27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard',
    32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove',
    36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
    40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl',
    46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
    51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair',
    57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet',
    62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone',
    68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator',
    73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
    78: 'hair drier', 79: 'toothbrush'
}

# Загрузка модели YOLO
model = YOLO("yolo11m-seg.pt")

# Инициализация клиента OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

async def get_ai_response(text: str) -> str:
    """Получение ответа от AI модели"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=512
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка при получении ответа от AI: {e}")
        return "Извините, произошла ошибка при обработке запроса."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Отправь мне фотографию, и я обработаю её с помощью YOLO. Мы не сохраняем фотографии пользователей, и не используем их для обучения."
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
    # Получаем ответ от AI
    response = await get_ai_response(update.message.text)
    await update.message.reply_text(response)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий"""
    try:
        # Получаем фото
        photo = await update.message.photo[-1].get_file()
        photo_bytes = await photo.download_as_bytearray()
        
        # Конвертируем в PIL Image
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Засекаем время начала обработки
        start_time = time.time()
        
        # Обрабатываем изображение с помощью YOLO
        results = model.predict(image, save=False, conf=0.25)
        
        # Получаем уникальные классы объектов
        detected_classes = set()
        for r in results:
            for c in r.boxes.cls:
                class_id = int(c.item())
                if class_id in CLASS_NAMES:
                    detected_classes.add(CLASS_NAMES[class_id])
        
        # Формируем промпт для LLM
        classes_text = ", ".join(detected_classes)
        prompt = f"На картинке есть {classes_text}, как ты думаешь что это за место?"
        
        # Получаем описание от LLM
        description = await get_ai_response(prompt)
        
        # Получаем обработанное изображение
        annotated_image = results[0].plot()
        
        # Вычисляем время обработки
        processing_time = time.time() - start_time
        
        # Исправляем цвета (BGR -> RGB)
        annotated_image = annotated_image[..., ::-1]
        
        # Конвертируем обратно в байты
        output = io.BytesIO()
        Image.fromarray(annotated_image).save(output, format='JPEG')
        output.seek(0)
        
        # Отправляем обработанное изображение с описанием
        await update.message.reply_photo(
            photo=output,
            caption=f"{description}\n\nВремя обработки: {processing_time:.2f} секунд"
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
