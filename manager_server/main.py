from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os, shutil
from fastapi import HTTPException
from manager_server.routes.files import router as files_router
from fastapi.staticfiles import StaticFiles
import colorlog
import logging

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger('manager_server')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory="manager_server/static"), name="static")
app.include_router(files_router)
templates = Jinja2Templates(directory="manager_server/templates")
DATA_DIR = "/app/datasheets"

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

@app.get("/")
def main_page(request: Request):
    files = [f for f in os.listdir(DATA_DIR) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
    logger.info(f"Main page accessed. Files listed: {files}")
    return templates.TemplateResponse("main.html", {"request": request, "files": files})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Upload attempt with disallowed file type: {file.filename}")
        return RedirectResponse("/", status_code=303)
    filename = os.path.basename(file.filename)
    save_path = os.path.join(DATA_DIR, filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Uploaded file: {filename}")
    return RedirectResponse("/", status_code=303)

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    ext = os.path.splitext(filename)[1].lower()
    if not os.path.isfile(file_path) or ext not in ALLOWED_EXTENSIONS:
        logger.error(f"Download failed. File not found or disallowed type: {filename}")
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")
    # 미디어 타입 결정
    media_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
    }
    media_type = media_types.get(ext, 'application/octet-stream')
    logger.info(f"Downloaded file: {filename}")
    return FileResponse(file_path, filename=filename, media_type=media_type) 