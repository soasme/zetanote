from uuid import uuid4

def generate_token():
    return uuid4().hex + uuid4().hex
