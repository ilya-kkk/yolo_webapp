from PIL import Image
from ultralytics import YOLO
import numpy as np

model = YOLO("yolov8n.pt")  # Загружаем легкую модель

def detect_objects(image: Image.Image) -> Image.Image:
    results = model.predict(np.array(image), save=False)
    annotated = results[0].plot()
    return Image.fromarray(annotated)
