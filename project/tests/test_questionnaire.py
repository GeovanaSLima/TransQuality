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
        app.dependency_overrides[get_current_user_from_token] = lambda: MockUser(username="testUser")
        response = client.get("/new-questionnaire", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 200  
        users_collection.delete_one({"username": "testUser"})

    # NEEDS TO BE FIXED
    # def test_save_responses(self):
    #     # Create a test user and insert into the database
    #     user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
    #     users_collection.insert_one(user)

    #     # Generate a test token for the created user
    #     token = generate_test_token(username="testUser")

    #     # Override the dependency to return the test user
    #     app.dependency_overrides[get_current_user_from_token] = lambda: MockUser(username="testUser")

    #     # Create a test response item
    #     response_item = {
    #         "form_id": 1,
    #         "question_number": 1,
    #         "answer": "Test Answer",
    #         "reserve": "Test Reserve",
    #         "observation": "Test Observation",
    #         "image": "Test Image",
    #     }

    #     # Make a request to the save_responses route with the test user's token and response item
    #     response = client.post("/save_responses", headers={"Authorization": f"Bearer {token}"}, json=response_item)
    #     print(response.content)
    #     # Check if the response indicates success
    #     assert response.status_code == 200
    #     assert response.json()["success"] == True

    #     # Clean up: Delete the test user, form, and response from the database
    #     users_collection.delete_one({"username": "testUser"})
    #     forms_collection.delete_one({"form_id": "testFormID", "user_id": str(user["_id"])})
    #     responses_collection.delete_one({"form_id": "testFormID", "user_id": str(user["_id"]), "question_number": 1})        