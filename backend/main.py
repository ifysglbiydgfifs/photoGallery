from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
import shutil, os

from database import Base, engine, SessionLocal
from models import Photo
from tasks import process_image

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Файл с таким именем уже существует")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    photo = Photo(filename=file.filename, filepath=file_path)
    db.add(photo)
    db.commit()
    db.refresh(photo)

    process_image.delay(file_path)

    return {"id": photo.id, "filename": photo.filename, "url": f"/uploads/{photo.filename}"}


@app.get("/photos/")
def list_photos(order_by: str = "date", db: Session = Depends(get_db)):
    valid_sort = {
        "name": Photo.filename,
        "size": Photo.filepath,
        "date": Photo.uploaded_at
    }

    if order_by not in valid_sort:
        raise HTTPException(status_code=400, detail="Некорректный параметр сортировки")

    if order_by == "name":
        photos = db.query(Photo).order_by(asc(Photo.filename)).all()
    elif order_by == "date":
        photos = db.query(Photo).order_by(desc(Photo.uploaded_at)).all()
    else:
        photos = db.query(Photo).all()
        photos.sort(key=lambda p: os.path.getsize(p.filepath) if os.path.exists(p.filepath) else 0)

    return [
        {
            "id": p.id,
            "filename": p.filename,
            "thumbnail_url": f"/uploads/{p.filename}",
            "full_url": f"/uploads/{p.filename}"
        }
        for p in photos
    ]


@app.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    if os.path.exists(photo.filepath):
        os.remove(photo.filepath)

    db.delete(photo)
    db.commit()
    return {"status": "deleted"}


@app.put("/photos/{photo_id}")
def rename_photo(photo_id: int, new_name: str, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не найдено")

    new_path = os.path.join(UPLOAD_DIR, new_name)
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail="Файл с таким именем уже существует")

    os.rename(photo.filepath, new_path)

    photo.filename = new_name
    photo.filepath = new_path
    db.commit()
    db.refresh(photo)

    return {"status": "renamed", "new_name": photo.filename}
