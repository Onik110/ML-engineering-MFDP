import pytest
import requests
import uuid

BASE_URL = "http://app:8080/api"

@pytest.fixture(scope="session")
def test_user():
    email = f"testuser_{uuid.uuid4().hex[:12]}@example.com"
    password = "strongpassword123"
    return {"email": email, "password": password}

@pytest.fixture(scope="session")
def auth_token(test_user):
    signup_resp = requests.post(f"{BASE_URL}/users/signup", json=test_user)

    if signup_resp.status_code == 409:
        pass
    elif signup_resp.status_code != 201:
        raise AssertionError(f"Signup failed: {signup_resp.status_code}, {signup_resp.text}")

    signin_resp = requests.post(
        f"{BASE_URL}/users/signin",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert signin_resp.status_code == 200, f"Signin failed: {signin_resp.text}"
    return signin_resp.json()["access_token"]