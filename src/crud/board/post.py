from uuid import UUID

from sqlalchemy.sql import select, functions, func
from sqlalchemy.orm import Session, aliased

from src.models.models import User, Post, PostCategory, PostContent


async def create_post(db: Session):
    ...


async def get_post_list(db: Session, category: str, keyword: str, skip: int, limit: int):
    category_tier_1 = aliased(PostCategory)
    category_subq = select(PostCategory) \
        .join(PostCategory.parent.of_type(category_tier_1)) \
        .where(category_tier_1.category == category) \
        .subquery(name='category_subq')
    Category = aliased(PostCategory, category_subq, name='Category')
    content_subq = select(functions.max(PostContent.version), PostContent) \
        .group_by(PostContent.id_post) \
        .subquery(name='Content')
    Content = aliased(PostContent, content_subq, name='Content')
    q = select(Post, Content, Category, User) \
        .join(Content) \
        .join(Category) \
        .join(User) \
        .where(Post.is_active == True)
    if keyword:
        keyword = f'%{keyword}%'
        q = q.where(
            Content.subject.ilike(keyword) |
            Content.content.ilike(keyword) |
            User.username.ilike(keyword)
        )
    total = await db.execute(select(func.count()).select_from(q))
    q = q.order_by(Post.date_create.desc()) \
        .offset(skip).limit(limit)
    res = await db.execute(q)
    return total.scalar(), res.all()


async def get_post(db: Session, id: UUID):
    content_subq = select(functions.max(PostContent.version), PostContent) \
        .group_by(PostContent.id_post) \
        .subquery(name='Content')
    Category = aliased(PostCategory, name='Category')
    Content = aliased(PostContent, content_subq, name='Content')
    q = select(Post, Content, Category, User) \
        .join(Content) \
        .join(Category) \
        .join(User) \
        .where(Post.id == id)
    res = await db.execute(q)
    return res.first()


async def update_post(db: Session):
    ...


async def del_post(db: Session):
    ...