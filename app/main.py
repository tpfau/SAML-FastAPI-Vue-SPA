from typing import Union
from static_files import SPAStaticFiles
from fastapi import FastAPI, Request, Response
from security.saml import prepare_from_fastapi_request, saml_settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from starlette.responses import RedirectResponse
import starlette.status as status
from security.jwt import create_access_token, get_current_user, TokenRequest
from urllib.parse import urlencode
import logging

app = FastAPI()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)


@app.middleware("http")
async def logger_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    log_message = f"Received request: {method} {path}"
    logging.info(log_message)
    response = await call_next(request)
    return response


@app.post("/auth/test")
async def auth_test(request: TokenRequest):
    # saml_settings = auth.get_settings()
    # metadata = saml_settings.get_sp_metadata()
    # errors = saml_settings.validate_metadata(metadata)
    # if len(errors) == 0:
    #   print(metadata)
    # else:
    #   print("Error found on Metadata: %s" % (', '.join(errors)))
    try:
        user = await get_current_user(request.token)
        return {"authed": True, "user": user}
    except Exception as e:
        return {"authed": False, "reason": str(e)}


@app.get("/data")
async def login(request: Request):
    req = await prepare_from_fastapi_request(request)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    # saml_settings = auth.get_settings()
    # metadata = saml_settings.get_sp_metadata()
    # errors = saml_settings.validate_metadata(metadata)
    # if len(errors) == 0:
    #   print(metadata)
    # else:
    #   print("Error found on Metadata: %s" % (', '.join(errors)))
    callback_url = auth.login()
    response = RedirectResponse(url=callback_url)
    return response


@app.get("/saml/login")
async def login(request: Request):
    req = await prepare_from_fastapi_request(request)
    auth = OneLogin_Saml2_Auth(req, saml_settings)
    # saml_settings = auth.get_settings()
    # metadata = saml_settings.get_sp_metadata()
    # errors = saml_settings.validate_metadata(metadata)
    # if len(errors) == 0:
    #   print(metadata)
    # else:
    #   print("Error found on Metadata: %s" % (', '.join(errors)))
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
            userdata = auth.get_attributes().copy()
            userdata["user"] = auth.get_nameid()
            tokenDic = {"token": create_access_token(userdata)}
            forwardAddress = f"/?{urlencode(tokenDic)}"
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
