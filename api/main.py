import os
import random

import psycopg2
import redis
from PIL import Image

redis_conn = redis.Redis(host="localhost", port=6379, db=0)
pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="postgres",
    user="pavelshishkin",
    password="postgres",
)


# Функция, которая будет забирать фотографии из папки и складывать их в очередь Redis
def enqueue_photos(path, redis_conn):
    for filename in os.listdir(path):
        with open(f"images/{filename}", "rb") as f:
            photo_data = f.read()
        redis_conn.lpush("photo_queue", photo_data)
    redis_conn.set("photo_queue_done", "True")


# Функция, которая будет извлекать из очереди фотографии и записывать их в бд Postgres
def process_photos(redis_conn, pg_conn):
    while True:
        photo_data = redis_conn.rpop("photo_queue")
        if photo_data is None:
            if redis_conn.get("photo_queue_done") == "True":
                break
            else:
                continue
        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO photos (created, photos) VALUES (NOW(), %s)",
                (photo_data,),
            )
            pg_conn.commit()


async def create_pics():
    # Создаем папку "images", если ее нет
    if not os.path.exists("images"):
        os.makedirs("images")

    # Создаем 30 картинок
    for i in range(30):
        # Создаем новое изображение
        img = Image.new("RGB", (40, 40))

        # Заполняем изображение случайными пикселями
        pixels = [
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for _ in range(40 * 40)
        ]
        img.putdata(pixels)

        # Сохраняем изображение в папке "images"
        img.save(f"images/img{i + 1}.jpg")
