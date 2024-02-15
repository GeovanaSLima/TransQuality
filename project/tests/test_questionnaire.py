from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from main import app, get_current_user_from_token, users_collection
from testsConfig import *


client = TestClient(app)

class TestQuestionnaire:
    def test_new_questionnaire(self):

        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        token = generate_test_token(username="testUser")
        app.dependency_overrides[get_current_user_from_token] = lambda: {"username": "testUser", "_id": "mock_id"}
        response = client.get("/new-questionnaire", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200  
        users_collection.delete_one({"username": "testUser"})

    def test_save_responses(self):
        user = {
            "name": "Jane Doe",
            "username": "testUser",
            "role": "user",
            "password": "testing",
            "created_at": datetime.today()
        }
        users_collection.insert_one(user)
        token = generate_test_token(username="testUser")
        app.dependency_overrides[get_current_user_from_token] = lambda: {"username": "testUser", "_id": "mock_id"}
        response_item = {
            "form_id": 1,
            "question_number": 1,
            "answer": "Test Answer",
            "reserve": "Test Reserve",
            "observation": "Test Observation",
            "image": "Test Image",
        }

        response = client.post("/save_responses", headers={"Authorization": f"Bearer {token}"}, json=response_item)
        print(response.json())
        print(response.status_code)


        assert response.status_code == 200
        assert response.json()["success"] == True
        
        users_collection.delete_one({"username": "testUser"})
        forms_collection.delete_one({"form_id": 1, "user_id": str(user["_id"])})
        responses_collection.delete_one({"form_id": 1, "user_id": str(user["_id"]), "question_number": 1})