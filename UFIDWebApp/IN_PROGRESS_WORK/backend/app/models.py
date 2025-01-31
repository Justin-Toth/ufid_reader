import uuid
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr

## LEAVING THIS IN FOR NOW (will remove later) ~ Justin
## Current STUDENT MODEL from current Application
"""
    STUDENT
        UFID (Primary Key)
        ISO  (Primary Key)
        FIRST_NAME
        LAST_NAME
        
        CLASS 1->8
"""

## Desired STUDENT MODEL for new Application
"""
    STUDENT
        UFID (Primary Key, Unique)
        ISO  (Primary Key, Unique)
        FULL_NAME
        EMAIL (Unique)
        COURSES (List of Courses) ... Come back to this ...
"""



# Student Model and CRUD Operations
class StudentBase(SQLModel):
    UFID: str = Field(primary_key=True, unique=True, min_length=8, max_length=8)
    ISO: str = Field(primary_key=True, unique=True, min_length=16, max_length=16)
    full_name: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, max_length=255)


# Database model, database table inferred from class name
class Student(StudentBase, table=True):
    course1: str | None
    course2: str | None
    course3: str | None
    course4: str | None


# Properties to receive via API on creation
class StudentCreate(StudentBase):
    UFID: str = Field(min_length=8, max_length=8)
    ISO: str = Field(min_length=16, max_length=16)
    full_name: str = Field(max_length=255)
    email: EmailStr = Field(max_length=255)

    course1: str | None = Field(default=None)
    course2: str | None = Field(default=None)
    course3: str | None = Field(default=None)
    course4: str | None = Field(default=None)


# Properties to receive via API on update, all are optional
class StudentUpdate(StudentBase):
    UFID: str | None = Field(default=None, min_length=8, max_length=8)
    ISO: str | None = Field(default=None, min_length=16, max_length=16)
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    
    course1: str | None = Field(default=None)
    course2: str | None = Field(default=None)
    course3: str | None = Field(default=None)
    course4: str | None = Field(default=None)


# Properties to return via API, UFID and ISO are always required
class StudentPublic(StudentBase):
    UFID: int
    ISO: int


class StudentsPublic(SQLModel):
    data: list[StudentPublic]
    count: int


# User Model and CRUD Operations
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, max_length=255)
    username: str = Field(unique=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_admin: bool = False
    is_teacher: bool = True


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str


# Properties to receive via API on creation (By Admin)
class UserCreate(UserBase):
    password: str = Field(min_length=5, max_length=40)


# Properties to receive via API on creation (By User)
class UserRegister(UserBase):
    email: EmailStr = Field(max_length=255)
    username: str = Field(max_length=255)
    password: str = Field(min_length=5, max_length=40)
    full_name: str = Field(default=None, max_length=255)


# Properties to receive via API on update (login creds), all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=5, max_length=40)


# Properties to receive via API on update (account info), all are optional
class UserUpdateMe(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update (password), all are required
class UserUpdatePassword(UserBase):
    current_password: str = Field(min_length=5, max_length=40)
    new_password: str = Field(min_length=5, max_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


"""
Currently have enough information to start building the application

ADD EXAM, KIOSK, AND TIMESHEET MODELS HERE LATER ~ Justin
    - Exams will be a table of exams to be held
    - Kiosks will be a table of kiosks to be used (raspi's) 
    - A timesheet will be linked to a course to log student attendance
        - Current application has a global timesheet
"""


# Extra General Models 
# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)