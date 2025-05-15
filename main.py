from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from models.model import generate_caption
import shutil
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("static/upload")
PROCESSED_DIR = Path("static/processed")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def save_image_info(image_info):
    existing_info = load_image_info()
    existing_info.update(image_info)
    with open("image_info.json", "w", encoding="utf-8") as json_file:
        json.dump(existing_info, json_file, ensure_ascii=False)


def load_image_info():
    try:
        with open("image_info.json", "r", encoding="utf-8") as json_file:
            image_info = json.load(json_file)
    except FileNotFoundError:
        image_info = {}
    except json.decoder.JSONDecodeError:
        image_info = {}
    return image_info


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("GET request to '/' endpoint")
    image_info = load_image_info()
    gallery = [{"filename": filename, "caption": caption} for filename, caption in image_info.items()]
    return templates.TemplateResponse("index.html", {"request": request, "gallery": gallery, "result": None})


@app.post("/process/", response_class=HTMLResponse)
async def process_image(request: Request, file: UploadFile = File(...)):
    logger.info(f"Uploading file: {file.filename}")
    file_location = UPLOAD_DIR / file.filename
    processed_file_location = PROCESSED_DIR / file.filename

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"File saved to {file_location}")

    caption = await generate_caption(str(file_location))
    logger.info(f"Generated caption: {caption}")

    processed_filename = file.filename
    processed_file_location = PROCESSED_DIR / processed_filename

    shutil.copyfile(file_location, processed_file_location)
    logger.info(f"File copied to {processed_file_location}")
    image_info = {processed_filename: caption}

    save_image_info(image_info)

    return await read_root(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
