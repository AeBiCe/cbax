from pathlib import Path
from fastapi import HTTPException
import os
import zipfile
from typing import List


COMIC_PATH = Path("./comics")
ALL_COMICS = [f.stem for f in COMIC_PATH.glob("*.cbz")]

# TODO: Decide if this and other modules should raise HTTP related exceptions


def get_comic_path(comic_id: int) -> Path:
    try:
        cbz_file_path = Path(f"{COMIC_PATH}/{ALL_COMICS[comic_id]}.cbz")
    except IndexError:
        raise HTTPException(status_code=404, detail="Comic not found")

    if not os.path.exists(cbz_file_path):
        raise HTTPException(status_code=404, detail="Comic not found")

    return cbz_file_path


def get_pages(cbz_file_path: Path) -> List[str]:
    with zipfile.ZipFile(cbz_file_path, "r") as zip_ref:
        pages = sorted(
            [
                name
                for name in zip_ref.namelist()
                if name.lower().endswith((".jpg", ".jpeg", ".png"))
            ]
        )

    if not pages:
        raise HTTPException(status_code=404, detail="No pages found in the comic")

    return pages
