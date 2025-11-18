from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app import crud, models
from app.core.config import SECRET_KEY, ALGORITHM # SECRET_KEY, ALGORITHM 직접 임포트
from app.db.session import SessionLocal # SessionLocal 임포트 경로 수정
from jose.exceptions import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login/token")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_user_from_token(db: Session, token: str) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = crud.crud_user.get(db, user_id=int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    return get_user_from_token(db=db, token=token)