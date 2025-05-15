from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from manager_server.utils.file_utils import get_folder_tree
import os
import shutil
import mimetypes
from pydantic import BaseModel

router = APIRouter()

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DATA_DIR = os.path.join(BASE_DIR, "datasheets")
DATA_DIR = "/app/datasheets"
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class CreateFolderRequest(BaseModel):
    parent: str
    name: str

class DeleteFolderRequest(BaseModel):
    parent: str

class DeleteItemRequest(BaseModel):
    path: str

@router.get("/api/files")
def api_files():
    """
    datasheets 폴더의 폴더+PDF 파일 트리 구조를 JSON으로 반환
    """
    tree = get_folder_tree(DATA_DIR)
    return tree

@router.get("/files")
def files_page(request: Request):
    """
    PDF 폴더 트리/업로드 폼 웹페이지 렌더링
    """
    return templates.TemplateResponse("main.html", {"request": request})

@router.get("/download/{relpath:path}")
def download_file(relpath: str):
    """
    상대경로로 PDF 파일 다운로드
    """
    file_path = os.path.abspath(os.path.join(DATA_DIR, relpath))
    # datasheets 폴더 내부에 있는지 확인
    if not file_path.startswith(DATA_DIR):
        raise HTTPException(status_code=403, detail="허용되지 않은 경로입니다.")
    # 파일 존재 확인
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")
    # 파일의 MIME 타입 자동 추정
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"
    return FileResponse(file_path, filename=os.path.basename(file_path), media_type=mime_type)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    target_folder: str = Form("")
):
    # PDF 확장자 체크
    if not file.filename.lower().endswith(".pdf"):
        return RedirectResponse("/files?error=pdfonly", status_code=303)
    filename = os.path.basename(file.filename)
    # 폴더 경로 처리
    parts = target_folder.split("/") if target_folder else []
    if parts and parts[0] == "datasheets":
        parts = parts[1:]
    save_dir = os.path.join(DATA_DIR, *parts)
    save_dir = os.path.abspath(save_dir)
    if not save_dir.startswith(DATA_DIR):
        return RedirectResponse("/files?error=badfolder", status_code=303)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse("/files", status_code=303)

@router.post("/create-folder")
async def create_folder(req: CreateFolderRequest):
    # parent: 상대경로, name: 새 폴더 이름
    parent = req.parent or ""
    parts = parent.split("/") if parent else []
    # 첫번째가 'datasheets'면 제거
    if parts and parts[0] == "datasheets":
        parts = parts[1:]
    parent_path = os.path.join(DATA_DIR, *parts)
    parent_path = os.path.abspath(parent_path)
    if not parent_path.startswith(DATA_DIR):
        raise HTTPException(status_code=403, detail="허용되지 않은 경로입니다.")
    new_folder_path = os.path.join(parent_path, req.name)
    if os.path.exists(new_folder_path):
        return JSONResponse({"error": "이미 존재하는 폴더입니다."}, status_code=400)
    try:
        os.makedirs(new_folder_path)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/delete-folder")
async def delete_folder(req: DeleteFolderRequest):
    parent = req.parent or ""
    parts = parent.split("/") if parent else []
    if parts and parts[0] == "datasheets":
        parts = parts[1:]
    folder_path = os.path.join(DATA_DIR, *parts)
    folder_path = os.path.abspath(folder_path)
    if not folder_path.startswith(DATA_DIR):
        raise HTTPException(status_code=403, detail="허용되지 않은 경로입니다.")
    if not os.path.isdir(folder_path):
        return JSONResponse({"error": "폴더가 존재하지 않습니다."}, status_code=404)
    try:
        shutil.rmtree(folder_path)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.post("/delete-item")
async def delete_item(req: DeleteItemRequest):
    path = req.path or ""
    parts = path.split("/") if path else []
    if parts and parts[0] == "datasheets":
        parts = parts[1:]
    abs_path = os.path.join(DATA_DIR, *parts)
    abs_path = os.path.abspath(abs_path)
    if not abs_path.startswith(DATA_DIR):
        raise HTTPException(status_code=403, detail="허용되지 않은 경로입니다.")
    if not os.path.exists(abs_path):
        return JSONResponse({"error": "파일 또는 폴더가 존재하지 않습니다."}, status_code=404)
    try:
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500) 