from testsConfig import *


class TestUser:
    def test_create_user(self):
        # Inserting User
        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        found_user = users_collection.find_one(filter={"username": "testUser"})
        
        # Assertions
        assert user["name"] == found_user["name"]

        # Delete test cases
        users_collection.delete_one({"username": "testUser"})
    