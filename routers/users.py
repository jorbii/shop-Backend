from fastapi import HTTPException, APIRouter
from sqlalchemy.orm import Session
from uuid import uuid4
from db.database import db

router = APIRouter()

@router.get("/me")
def user_info(session: Session):
