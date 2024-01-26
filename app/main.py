from typing import Union
from static_files import SPAStaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Request, Response, Security
from security.saml import prepare_from_fastapi_request, saml_settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from security.session import SessionHandler
from security.auth import SAMLSessionBackend
import starlette.status as status

from security.jwt import (
    create_access_token,
    get_current_user,
    TokenRequest,
    get_authed_user,
    User,
    api_key_header,
)
from urllib.parse import urlencode
import logging

# Debugging imports
import traceback

session_handler = SessionHandler()
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string", max_age=None)
app.add_middleware(AuthenticationMiddleware, backend=SAMLSessionBackend)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


@app.middleware("http")
async def logger_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    log_message = f"Received request: {method} {path}"
    logging.info(log_message)
    logging.info(request.headers)
    response = await call_next(request)
    return response


@app.middleware("http")
async def logger_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    log_message = f"Received request: {method} {path}"
    logging.info(log_message)
    logging.info(request.headers)
    response = await call_next(request)
    return response


@app.post("/auth/test")
async def auth_test(request: Request):
    # Obtain the auth manually here, because we want to provide
    # Information about the authentication status, and using security would make this fail with Unauthorized
    # Responses...
    if request.user.is_authenticated:
        return {"authed": True, "user": request.user.username}
    else:
        return {"authed": False, "reason": "No Token provided"}


@app.get("/data")
async def getData(request: Request, user: User = Security(get_authed_user)):
    return user


@app.get("/saml/login")
async def login(request: Request):
    req = await prepare_from_fastapi_request(request)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    callback_url = auth.login()
    response = RedirectResponse(url=callback_url)
    return response


@app.post("/saml/acs")
async def saml_callback(request: Request):
    req = await prepare_from_fastapi_request(request, True)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    auth.process_response()  # Process IdP response
    errors = auth.get_errors()  # This method receives an array with the errors
    if len(errors) == 0:
        if not auth.is_authenticated():
            # This check if the response was ok and the user data retrieved or not (user authenticated)
            return "User Not authenticated"
        else:
            sessionData = {}
            sessionData["samlUserdata"] = auth.get_attributes()
            sessionData["samlNameId"] = auth.get_nameid()
            sessionData["samlNameIdFormat"] = auth.get_nameid_format()
            sessionData["samlNameIdNameQualifier"] = auth.get_nameid_nq()
            sessionData["samlNameIdSPNameQualifier"] = auth.get_nameid_spnq()
            sessionData["samlSessionIndex"] = auth.get_session_index()
            session_key = session_handler.create_session(sessionData)
            req.session["key"] = session_key
            forwardAddress = f"/"
            return RedirectResponse(
                url=forwardAddress, status_code=status.HTTP_303_SEE_OTHER
            )
    else:
        logging.error(
            "Error when processing SAML Response: %s %s"
            % (", ".join(errors), auth.get_last_error_reason())
        )
        return "Error in callback"


@app.get("/saml/metadata")
async def metadata():
    metadata = saml_settings.get_sp_metadata()
    return Response(content=metadata, media_type="text/xml")


# This has to be the very last route!!
app.mount("/", SPAStaticFiles(directory="frontend/dist", html=True), name="FrontEnd")
