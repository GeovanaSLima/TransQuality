from testsConfig import *

class MockUser:
    def __init__(self, username: str):
        self.username = username

# Cria um token fake para o usuário
def generate_test_token(username: str):
    expiration = datetime.utcnow() + timedelta(days=1)
    data = {"sub": username, "exp": expiration}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

app.dependency_overrides[get_current_user_from_token] = lambda: MockUser(username="test_user")


class TestUser:
    def test_create_user(self):
        user = {"name": "Jane Doe", "username": "testUser", "role": "user", "password": "testing", "created_at": datetime.today()}
        users_collection.insert_one(user)

        found_user = users_collection.find_one(filter={"username": "testUser"})
        assert user["name"] == found_user["name"]
        users_collection.delete_one({"username": "testUser"})

    # NEEDS FIXING
    def test_update_password(self):
        user = {
            "_id": ObjectId(),
            "username": "testUser",
            "password": Hasher.get_password_hash("testing")
        }

        users_collection.insert_one(user)

        print("Original Password:", user["password"])
        test_token = jwt.encode({"sub": "testUser"}, settings.JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {test_token}"}

        response = test_client.put(
            "/update-password",
            headers=headers,
            json={"new_password": "new_password", "current_password": "testing"}
        )

        # Modifique a assertiva para verificar o código de status correto
        assert response.status_code == 422  # 422 Unprocessable Entity

        # Verifique se a resposta contém informações sobre o redirecionamento
        assert b"302 Found" in response.content
        assert b"/home" in response.content
