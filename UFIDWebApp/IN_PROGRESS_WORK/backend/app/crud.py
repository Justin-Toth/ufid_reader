from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate, Student, StudentCreate, StudentUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user

def get_user_by_username(*, session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email_or_username: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email_or_username)
    if not db_user:
        db_user = get_user_by_username(session=session, username=email_or_username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_student(*, session: Session, student_create: StudentCreate) -> Student:
    db_obj = Student.model_validate(student_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_student(*, session: Session, db_student: Student, student_in: StudentUpdate) -> Any:
    student_data = student_in.model_dump(exclude_unset=True)
    db_student.sqlmodel_update(student_data)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


def get_student_by_UFID(*, session: Session, UFID: int) -> Student | None:
    statement = select(Student).where(Student.UFID == UFID)
    db_student = session.exec(statement).first()
    return db_student


def get_student_by_ISO(*, session: Session, ISO: int) -> Student | None:
    statement = select(Student).where(Student.ISO == ISO)
    db_student = session.exec(statement).first()
    return db_student



"""
Future Functions to add

(We can attach exams to a course?)
create_exam
update_exam


yap yap yap ~ Justin

"""