from fastapi import  Depends, HTTPException, Path, APIRouter
from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users
from database import get_db
from routers.auth import get_current_user
import logging

router = APIRouter(
    prefix='/users',
    tags=['users'],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

logger = logging.getLogger(__name__)

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UserPhoneRequest(BaseModel):
    phone_number: str

@router.get('/', status_code=status.HTTP_200_OK)
async def get(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    return db.query(Users).filter(Users.id == user.get('user_id')).first()


@router.put('/change_password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(db: db_dependency, user: user_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")


    user_model.hashed_password = bcrypt_context.hash(user_verification.password)
    db.add(user_model)
    db.commit()

@router.put('/update_phone', status_code=status.HTTP_204_NO_CONTENT)
async def update_phone(db: db_dependency, user: user_dependency, user_phone_request: UserPhoneRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication credentials were not provided")
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()

    user_model.phone_number = user_phone_request.phone_number
    db.add(user_model)
    db.commit()
