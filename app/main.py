from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database.connection import get_db

app = FastAPI(title="account-book-api")

@app.get("/")
async def main(
    db: Session = Depends(get_db)
):
    return {"message": "Hello World"}
