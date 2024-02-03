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


