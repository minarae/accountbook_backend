from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database.connection import get_db
from .database import models
from .routers import members

app = FastAPI(title="account-book-api")

app.include_router(members.router)

@app.get("/")
async def main(
    db: Session = Depends(get_db)
):
    return {"message": "Hello World"}
