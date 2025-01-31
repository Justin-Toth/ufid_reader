from collections.abc import Generator
from typing import Annotated

import jwt
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError 
from pydantic import ValidationError
from sqlmodel import Session

from app.core.security import ALGORITHM
from app.core.config import settings
from app.core.db import get_db
from app.models import User

# Fix this for the OAuth2PasswordBearer (IDK)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/login/test"
)

        
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = payload.get("sub")
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user_id = uuid.UUID(token_data)
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="The user does not have enough privileges",
        )
    return current_user