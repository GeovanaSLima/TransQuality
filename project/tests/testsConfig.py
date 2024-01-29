import os
import sys
import inspect

from fastapi.testclient import TestClient

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from main import *


############# MongoDB Testing configuration
def get_test_client():
    return MockMongoClient(settings.DATABASE_URL) 


test_client = TestClient(app)

app.dependency_overrides[get_prod_client] = get_test_client


# Cria uma instância do banco de dados simulado usando o mesmo nome
test_db = get_test_client().get_database(settings.MONGO_INITDB_DATABASE)

responses_collection = test_db.responses
forms_collection = test_db.forms
users_collection = test_db.users
questions_collection = test_db.questions

users_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
forms_collection.create_index([("form_id", pymongo.ASCENDING)], unique=True)
questions_collection.create_index([("question_number", pymongo.ASCENDING)], unique=True)
