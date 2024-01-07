from mongoengine import Document, IntField, StringField, ReferenceField, BooleanField, DateTimeField
from pydantic import BaseModel
from typing import Any


class BaseDocument(Document):
    # Common fields
    id = IntField(primary_key=True, required=True)

    # Custom behavior
    def save(self, *args, **kwargs):
        # Add custom save behavior if needed
        super().save(*args, **kwargs)

    # Generate collection name from classname
    @classmethod
    def _get_collection_name(cls):
        return cls.__name__.lower()
    
    meta = {'collection': _get_collection_name, 'allow_inheritance': True, 'abstract': True}


class User(Document):
    name = StringField(required=True)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    role = StringField(required=True)

    meta = {'collection': 'users'}


class Token(BaseModel):
    access_token: str
    token_type: str


class Form(BaseDocument):
    user_id = ReferenceField(User, required=True)
    complete = BooleanField(default=False)
    n_question = IntField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    meta = {'collection': 'forms'}


class Questionnaire(BaseDocument):
    form_id = ReferenceField(Form, required=True)
    user_id = ReferenceField(User, required=True)
    question_number = IntField(required=True)
    theme = StringField(required=True)
    location = StringField(required=True)
    question = StringField(required=True)
    answer = StringField(required=True)
    reserve = StringField()
    observation = StringField()

    meta = {'collection': 'responses'}
