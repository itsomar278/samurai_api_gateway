import jwt
import requests


def decode_jwt_payload(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {e}")


def is_authenticated(token):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/accounts/token/verify/",
            json={"token": token}
        )
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException as e:
        return False
