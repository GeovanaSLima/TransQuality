from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, get_current_user_from_token, users_collection
from testsConfig import *


client = TestClient(app)

class TestQuestionnaire:
    def test_new_questionnaire(self):
        # Inserting User
        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        token = generate_test_token(username="testUser")
        app.dependency_overrides[get_current_user_from_token] = lambda: {"username": "testUser", "_id": "mock_id"}

        response = client.get("/new-questionnaire", headers={"Authorization": f"Bearer {token}"})

        # Assertions
        assert response.status_code == 200  

        # Delete test cases
        users_collection.delete_one({"username": "testUser"})

    def test_save_responses(self):
        # User and Response Dictionaries
        user = {
            "name": "Jane Doe",
            "username": "testUser",
            "role": "user",
            "password": "testing",
            "created_at": datetime.today()
        }

        response_item = {
            "form_id": 1,
            "question_number": 1,
            "answer": "Test Answer",
            "reserve": "Test Reserve",
            "observation": "Test Observation",
            "image": "Test Image",
        }

        users_collection.insert_one(user)

        token = generate_test_token(username="testUser")
        app.dependency_overrides[get_current_user_from_token] = lambda: {"username": "testUser", "_id": "mock_id"}
        
        response = client.post("/save_responses", headers={"Authorization": f"Bearer {token}"}, json=response_item)

        # Assertions
        assert response.status_code == 200
        assert response.json()["success"] == True
        
        # Deleting test cases
        users_collection.delete_one({"username": "testUser"})
        forms_collection.delete_one({"form_id": 1, "user_id": str(user["_id"])})
        responses_collection.delete_one({"form_id": 1, "user_id": str(user["_id"]), "question_number": 1})

    from bson import ObjectId

    def test_delete_form(self):
        # Inserting User and Form
        user = {
            "name": "Jane Doe",
            "username": "testUser",
            "role": "user",
            "password": "testing",
            "created_at": datetime.today()
        }

        users_collection.insert_one(user)

        response_item = {
            "form_id": 1,
            "user_id": user["_id"],
            "question_number": 1,
            "answer": "Test Answer",
            "reserve": "Test Reserve",
            "observation": "Test Observation",
            "image": "Test Image",
        }

        token = generate_test_token(username="testUser")
        app.dependency_overrides[get_current_user_from_token] = lambda: {"username": "testUser", "_id": "mock_id"}

        forms_collection.insert_one(response_item)

        print(f"Here is the form: {forms_collection.find_one({'form_id': response_item['form_id']})}")

        # Calling the Delete Route
        response = client.get(f"/delete/{response_item['form_id']}", headers={"Authorization": f"Bearer {token}"})

        # Assertions
        assert response.status_code == 200

        print(f"form not deleted: {forms_collection.find_one({'form_id': response_item['form_id']})}")
        # Delete test cases
        users_collection.delete_one({"username": "testUser"})


