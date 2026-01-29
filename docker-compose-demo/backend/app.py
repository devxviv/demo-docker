from fastapi import FastAPI
import psycopg2
import os
import time

app = FastAPI()

# Simple db connection with retry
def get_db():
    while True:
        try:
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "database"),
                user=os.getenv("DB_USER", "user"),
                password=os.getenv("DB_PASS", "password"),
                dbname=os.getenv("DB_NAME", "demodb")
            )
        except:
            time.sleep(1)

# Create table on startup
@app.on_event("startup")
def startup():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS items (name text)")
            conn.commit()

@app.get("/items")
def read_items():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM items")
            return [row[0] for row in cur.fetchall()]

@app.post("/items")
def create_item(name: str):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO items (name) VALUES (%s)", (name,))
            conn.commit()
    return "OK"
