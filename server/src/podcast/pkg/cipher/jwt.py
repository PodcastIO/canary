import logging

import jwt
from podcast.config.conf import ConfigFile


class Jwt:
    Headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    def __init__(self, **kwargs):
        self.payload: dict = kwargs.get("payload")
        self.token: str = kwargs.get("token")

    def encrypt_auth_token(self):
        return jwt.encode(payload=self.payload, key=ConfigFile.get_jwt_salt(), algorithm=Jwt.Headers["alg"],
                          headers=Jwt.Headers)

    def decrypt_auth_token(self):
        return jwt.decode(self.token, ConfigFile.get_jwt_salt(), algorithms=Jwt.Headers["alg"],
                          headers=Jwt.Headers)

    def encode_share_token(self):
        return jwt.encode(payload=self.payload, key=ConfigFile.get_podcast_share_secret_salt(), algorithm=Jwt.Headers["alg"],
                          headers=Jwt.Headers)

    def decode_share_token(self):
        return jwt.decode(self.token, ConfigFile.get_book_podcast_secret_salt(), algorithms=Jwt.Headers["alg"],
                          headers=Jwt.Headers)
