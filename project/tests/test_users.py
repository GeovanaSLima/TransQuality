from testsConfig import *

class MockUser:
    def __init__(self, username: str):
        self.username = username

# Cria um token fake para o usuário
fake_token = "fake_token"

app.dependency_overrides[get_current_user_from_token] = lambda: MockUser(username="test_user")


class TestUser:
    def test_create_user(self):
        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        found_user = users_collection.find_one(filter={"username": "testUser"})
        assert user["name"] == found_user["name"]
        users_collection.delete_one({"username": "testUser"})
