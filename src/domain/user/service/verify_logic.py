from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import NotUniqueError
from src.db.query.user import user_read

from ..model import user_request


async def verify_user_create(
    *,
    db: AsyncSession,
    data: user_request.UserCreateRequest,
) -> None:
    user_list = await user_read.read_user_by_name_email(
        db=db,
        name=data.name,
        email=data.email,
    )

    username_conflict = [u for u in user_list if data.name == u.name]
    if username_conflict:
        raise NotUniqueError(field=data.name)

    email_conflict = [u for u in user_list if data.email == u.email]
    if email_conflict:
        raise NotUniqueError(field=data.email)


async def verify_user_update(
    *,
    db: AsyncSession,
    data: user_request.UserCurrent,
) -> None:
    user_list = await user_read.read_user_by_name_email(
        db=db,
        name=data.name,
        email=data.email,
    )

    email_conflict = [u for u in user_list if data.email == u.email and data.id != u.id]
    if email_conflict:
        raise NotUniqueError(field=data.email)

    name_conflict = [u for u in user_list if data.name == u.name and data.id != u.id]
    if name_conflict:
        raise NotUniqueError(field=data.name)
