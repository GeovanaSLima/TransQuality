from __future__ import annotations

from app.imports import *


class ResponseItem(BaseModel):
    form_id: int
    user_id: Optional[str] = None
    question_number: int
    answer: str
    reserve: str = ""
    observation: str = ""
    image: Optional[str]

    class Config:
        orm_mode = True


class ShowQuestionnaire(ResponseItem):
    QuestionNumber: int
    form_id: int
    Theme: str
    Location: str
    Question: str
    Answer: str
    Reserve: str = ""
    Observation: str = ""
    Images: Optional[List[UploadFile]]
    user_id: str

    class Config():  
        orm_mode = True


class FormItem(BaseModel):
    form_id: int
    user_id: str
    complete: bool
    minor: int
    major: int
    critical: int
    question_number: int
    created_at: datetime

    class Config:
        orm_mode = True



class UserBaseSchema(BaseModel):
    name: str
    username: str
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    name: str
    password: str
    role: str


class ShowUser(BaseModel):
    username: str
    name: str
    role: str

    class Config:
        orm_mode = True


class Question(BaseModel):
    question_number: int
    question: str
    theme: str
    location: str

    class Config:
        orm_mode = True