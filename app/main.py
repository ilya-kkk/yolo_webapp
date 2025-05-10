from fastapi import FastAPI, File, UploadFile
from app.inference import detect_objects
from PIL import Image
from io import BytesIO
import uvicorn
import os

app = FastAPI()

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = Image.open(BytesIO(await file.read()))
    result_img = detect_objects(image)

    buf = BytesIO()
    result_img.save(buf, format="JPEG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")
