from sqlmodel import Session, create_engine, select
from collections.abc import Generator

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

engine = create_engine("sqlite:///./app/data/test.db")

def init_db(session: Session) -> None:
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_admin=True,
        )
        user = crud.create_user(session=session, user_create=user_in)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session