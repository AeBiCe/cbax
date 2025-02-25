from typing import List
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import zipfile
from pathlib import Path
import os
from io import BytesIO

app = FastAPI()
comic_router = APIRouter()

COMIC_PATH = Path("./comics")
ALL_COMICS = [f.stem for f in COMIC_PATH.glob("*.cbz")]

def get_comic_path(comic_id: int) -> Path:
    try:
        cbz_file_path = Path(f"{COMIC_PATH}/{ALL_COMICS[comic_id]}.cbz")
    except IndexError:
        raise HTTPException(status_code=404, detail="Comic not found")
    
    if not os.path.exists(cbz_file_path):
        raise HTTPException(status_code=404, detail="Comic not found")
    
    return cbz_file_path

def get_pages(cbz_file_path: Path) -> List[str]:
    with zipfile.ZipFile(cbz_file_path, 'r') as zip_ref:
        images = sorted([name for name in zip_ref.namelist() if name.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if not images:
        raise HTTPException(status_code=404, detail="No images found in the comic")
    
    return images

@comic_router.get("/comics")
def list_comics():
    return {"comics": ALL_COMICS}

@comic_router.get("/comic/{comic_id}")
def read_comic(cbz_file_path: Path = Depends(get_comic_path)):
    return {"pages": get_pages(cbz_file_path)}

@comic_router.get("/comic/{comic_id}/page/{page_number}")
def get_comic_page(page_number: int, cbz_file_path: Path = Depends(get_comic_path)):
    pages = get_pages(cbz_file_path)
    
    if page_number < 1 or page_number > len(pages):
        raise HTTPException(status_code=404, detail="Page number out of range")
    
    page = pages[page_number - 1]
    with zipfile.ZipFile(cbz_file_path, 'r') as zip_ref:
        page_data = zip_ref.read(page)
    
    return StreamingResponse(BytesIO(page_data), media_type="image/jpeg")

app.include_router(comic_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
