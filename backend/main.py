from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import shutil, os

from database import Base, engine, SessionLocal
from models import Photo
from tasks import process_image

UPLOAD_DIR = "/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Отдаём статику (миниатюры/фото)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Dependency для работы с БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = next(get_db())):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # сохраняем файл
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # запись в БД
    photo = Photo(filename=file.filename, filepath=file_path)
    db.add(photo)
    db.commit()
    db.refresh(photo)

    # запускаем фоновую обработку
    process_image.delay(file_path)

    return {"id": photo.id, "filename": photo.filename, "url": f"/uploads/{photo.filename}"}

@app.get("/photos/")
def list_photos(db: Session = next(get_db())):
    photos = db.query(Photo).all()
    return [
        {"id": p.id, "filename": p.filename, "thumbnail_url": f"/uploads/{p.filename}", "full_url": f"/uploads/{p.filename}"}
        for p in photos
    ]
