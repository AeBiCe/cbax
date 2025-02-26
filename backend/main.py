from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import zipfile
from pathlib import Path
from io import BytesIO
from backend.comic import ALL_COMICS, get_comic_path, get_pages

app = FastAPI()
comic_router = APIRouter()


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
    with zipfile.ZipFile(cbz_file_path, "r") as zip_ref:
        page_data = zip_ref.read(page)

    return StreamingResponse(BytesIO(page_data), media_type="image/jpeg")


app.include_router(comic_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
