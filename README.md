## Description

This is a basic Backed-frontend split for an application using vue as front-end and a fastAPI backend performing SAML authentication.

## References

- https://github.com/ais-one/fastapi-saml
- https://fastapi.tiangolo.com/
- https://github.com/onelogin/python3-saml
- **Need Not Read This** https://dev.to/zenika/fastapi-saml-on-keycloak-49l6

## Requirements

- Docker
- Python 3.8+

## Setup

### Create certificates

```
mkdir app/saml/certs
cd app/saml/certs
openssl req -new -x509 -days 3652 -nodes -out sp.crt -keyout sp.key
```

Enter the details requested

### Set up SAML IdP, using keycloak (if no external IdP available)

Refer to the following repository README.md for running Keycloak using docker-compose and setting up a SAML2 client on Keycloak

The following is adapted from the readme on this repo:
https://github.com/ais-one/cookbook/tree/main/docker-devenv/keycloak

**Instructions**

#### Login

URL: http://127.0.0.1:8081/
Administrayopm Console

- Username: admin
- password: admin

#### Keycloak Setup:

** Realm creation **

- top left (master) -> create Realm
  - Realm name : test

** Obtain realm Certificate **

- Configure(left menu) -> Realm Settings -> Endpoints - SAML 2.0 .. Metadata
  - copy `<ds:x509Certificate>` tab data
  - paste the data under the project folders `app/saml/settings.json` replacing the `idp -> x509cert` field

** Set up a client **

- Start the app:
  ```
    cd app
    gunicorn main:app --bind 0.0.0.0:3000 -k uvicorn.workers.UvicornWorker --workers 1
  ```
- go to "127.0.0.1:3000/saml/metadata"
- save the file as metadata.xml
- In the keycloak administration console:
  - Manage (left Menu) -> Clients -> Import Client -> Browse
  - select the metadata file you created

** Configure the client **

- Manage (left menu) -> Client Scopes -> role_list -> Mappers -> role_list
  - Activate "single role attribute"
  - Save
- Manage -> Clients -> Roles -> Create Role
  - Role Name : User -> Save

** Create a user **

- Manage (left Menu) -> Users -> Add User
  - UserName : test-user
  - Create
- Manage (left Menu) -> Users -> test-user -> Credentials -> Add Password
  - (select a password), deactivate temporary
- Manage (left Menu) -> Users -> test-user -> Role Mapping -> Assign role -> Filter By Clients
  - Select the User role created before

This should be it

## SAML Sample Application Installation

```cmd
python -m venv dev
dev\Scripts\activate

pip install fastapi uvicorn[standard] python3-saml python-multipart

uvicorn main:app --reload --port 3000
```

## Testing

With application running, navigate to http://127.0.0.1:3000/api/saml/login on the browser to initiate redirect to IDP

SAML Response is sent to http://127.0.0.1:3000/api/saml/callback

## API Documentation

With application running, navigate to [http://127.0.0.1:3000/docs](http://127.0.0.1:3000/docs) on the browser for API documentation
