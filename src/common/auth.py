from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.common import configs
from src.db import database
from src.db.query.user import user_read

config = configs.config.fastapi
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


async def verify_user_state(*, user: UserEntity):
    for state in user.state:
        if str(state.name) == user_enum.UserStateEnum.BLOCKED:
            raise BlockedUserError
        elif str(state.name) == user_enum.UserStateEnum.INACTIVATE:
            # TODO
            ...


async def get_current_user(
    *,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(database.get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=config.auth.secret_key,
            algorithms=config.auth.algorithm,
        )
        username = str(payload.get("sub"))
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = await user_read.read_user_by_name(db=db, name=username)
        if user is None:
            raise credentials_exception
        return user
