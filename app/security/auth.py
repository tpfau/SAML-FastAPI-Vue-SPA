from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    BaseUser,
)
from starlette.middleware import Middleware
from .session import SessionHandler


class SAMLUser(SimpleUser):
    def __init__(self, username: str, userdata: dict):
        self.username = username
        self.data = userdata

    def get_user_data(self):
        return self.data


class SAMLSessionBackend(AuthenticationBackend):
    def __init__(self, session_handler: SessionHandler):
        self.session_handler = session_handler

    async def authenticate(self, conn):
        try:
            if conn.session == None:
                return
        except AssertionError:
            return
        # check for authentication:
        if not "key" in conn.session:
            return
        data = self.session_handler.get_session_data(conn.session["key"])
        return AuthCredentials(["authenticated"]), SAMLUser(data["username"], data)
