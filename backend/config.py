from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
import os

sslrootcert = "ca_aiven.pem"
load_dotenv()

urlpg = str(os.environ.get("PG_URL"))
PG_URL = urlpg + sslrootcert


engine = create_engine(PG_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
