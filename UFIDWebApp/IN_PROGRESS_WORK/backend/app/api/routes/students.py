from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    SessionDep,
    get_current_admin,
)
from app.models import (
    Student,
    StudentCreate,
    StudentUpdate,
    StudentPublic,
    StudentsPublic,
    Message,

)

router = APIRouter(prefix="/students", tags=["students"])

@router.get(
    "/",
    dependencies=[Depends(get_current_admin)],
    response_model=StudentsPublic,
)
def read_students(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve students.
    """

    count_statement = select(func.count()).select_from(Student)
    count = session.exec(count_statement).one()

    statement = select(Student).offset(skip).limit(limit)
    students = session.exec(statement).all()

    return StudentsPublic(data=students, count=count)


@router.post(
    "/create", 
    dependencies=[Depends(get_current_admin)], 
    response_model=StudentPublic
)
def create_student(*, session: SessionDep, student_in:StudentCreate) -> Any:
    """
    Create new student.
    """
    student = crud.get_student_by_UFID(session=session, UFID=student_in.UFID)
    if not student:
        student = crud.get_student_by_ISO(session=session, ISO=student_in.ISO)
    if student:
        raise HTTPException(
            status_code=400,
            detail="The student with this UFID/ISO already exists in the system.",
        )
    student = crud.create_student(session=session, student_create=student_in)
    return student


@router.patch(
        "/{student_UFID}", 
        dependencies=[Depends(get_current_admin)], 
        response_model=StudentPublic
    )
def update_student(
    *,
    session: SessionDep,
    student_UFID: str,
    student_in: StudentUpdate,
) -> Any:
    """
    Update a student.
    """
    db_student = crud.get_student_by_UFID(session=session, UFID=student_UFID)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    db_student = crud.update_student(session=session, db_student=db_student, student_in=student_in)
    return db_student

@router.delete("/{student_UFID}", dependencies=[Depends(get_current_admin)])
def delete_student(session: SessionDep, student_UFID: str) -> Message:
    """
    Delete a student.
    """
    db_student = crud.get_student_by_UFID(session=session, UFID=student_UFID)
    if not db_student:
        raise HTTPException(
            status_code=404, detail="Student not found"
        )
    session.delete(db_student)
    session.commit()
    return Message(message="Student deleted")