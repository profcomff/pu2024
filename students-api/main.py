from typing import Self

import starlette.requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, TypeAdapter, model_validator


class StudentsAPIError(Exception):
    pass


class StudentNotFoundError(StudentsAPIError):
    pass


class StudentAlreadyExistsError(StudentsAPIError):
    pass


class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    course: int
    card: int

    @model_validator(mode="after")
    def val_course(self) -> Self:
        if not 1 <= self.course <= 6:
            raise ValueError("Course should be in [1, 6]")
        return self

    @model_validator(mode="after")
    def val_card(self) -> Self:
        if len(str(self.card)) != 6:
            raise ValueError("Card number length have to be equal to 6")
        return self


class StudentGet(StudentCreate):
    id: int


STUDENTS: dict[int, dict[str, str | int]] = {}
COUNT = 0


def generate_unigue_id():
    global COUNT
    COUNT += 1
    return COUNT


def get_student(id: int) -> StudentGet:
    student = STUDENTS.get(id)
    if not student:
        raise StudentNotFoundError()
    return StudentGet.model_validate({"id": id, **student})


def check_student_already_existing(student: StudentCreate) -> None:
    for existing_student in STUDENTS.values():
        if existing_student["card"] == student.card:
            raise StudentAlreadyExistsError()


def delete_student(id: int) -> None:
    try:
        del STUDENTS[id]
    except KeyError:
        raise StudentNotFoundError()


def get_students(course: int | None = None) -> list[StudentGet]:
    adapter = TypeAdapter(list[StudentGet])
    if course:
        students = [
            {"id": _id, **STUDENTS[_id]}
            for _id in STUDENTS
            if STUDENTS[_id]["course"] == course
        ]
    else:
        students = [{"id": _id, **STUDENTS[_id]} for _id in STUDENTS]
    return adapter.validate_python(students)


def create_student(student: StudentCreate) -> StudentGet:
    check_student_already_existing(student)
    new_id = generate_unigue_id()
    STUDENTS[new_id] = student.model_dump()
    return get_student(new_id)


app = FastAPI(title="Students API")


@app.exception_handler(StudentNotFoundError)
async def not_found_error(
    request: starlette.requests.Request, exc: StudentNotFoundError
):
    return JSONResponse({"error": "Student not found"}, status_code=404)


@app.exception_handler(StudentAlreadyExistsError)
async def already_exists_error(
    request: starlette.requests.Request, exc: StudentAlreadyExistsError
):
    return JSONResponse(
        {"error": "Student already exists"},
        status_code=409,
    )


@app.exception_handler(Exception)
async def internal_server_error(request: starlette.requests.Request, exc: Exception):
    return JSONResponse({"error": "Error"}, status_code=500)


@app.post("/student", response_model=StudentGet)
def create(student: StudentCreate):
    return create_student(student)


@app.get("/student/{id}", response_model=StudentGet)
def get(id: int) -> StudentGet:
    return get_student(id)


@app.get("/student", response_model=list[StudentGet])
def get_all(course: int | None = None):
    return get_students(course)


@app.delete("/student/{id}")
def delete(id: int):
    return delete_student(id)


uvicorn.run(app, host='0.0.0.0')
