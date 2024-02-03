from testsConfig import *


class TestUser:
    def test_create_user(self):
        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        found_user = users_collection.find_one(filter={"username": "testUser"})
        assert user["name"] == found_user["name"]
        users_collection.delete_one({"username": "testUser"})

    