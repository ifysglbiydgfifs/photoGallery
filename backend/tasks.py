import os
from celery import Celery

redis_host = os.environ.get("REDIS_HOST", "localhost")

celery = Celery(
    "tasks",
    broker=f"redis://{redis_host}:6379/0",
    backend=f"redis://{redis_host}:6379/0"
)

@celery.task
def process_image(file_path):
    # здесь будет генерация описаний / тегов через нейронку
    print(f"Processing image: {file_path}")
    return {"file_path": file_path, "status": "ok"}
