import threading

from api.main import enqueue_photos, process_photos, redis_conn, pg_conn, create_pics
from fastapi import FastAPI

app = FastAPI()


@app.post("/start_threads")
async def start_threads():
    enqueue_thread = threading.Thread(
        target=enqueue_photos, args=("images", redis_conn)
    )
    process_thread = threading.Thread(target=process_photos, args=(redis_conn, pg_conn))
    enqueue_thread.start()
    process_thread.start()
    return {"message": "Threads started"}


@app.post("/stop_threads")
async def stop_threads():
    redis_conn.set("photo_queue_done", "True")
    return {"message": "Threads stopped"}


@app.post("/create_pics")
async def create_pictures():
    await create_pics()
    return {"message": "30 pictures was created"}


# Закрываем соединения с Redis и Postgres при завершении работы приложения
@app.on_event("shutdown")
async def shutdown_event():
    redis_conn.close()
    pg_conn.close()
