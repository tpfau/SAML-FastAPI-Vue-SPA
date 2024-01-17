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

https://github.com/ais-one/vue-crud-x/tree/master/docker-devenv/keycloak

**Note:**

- please follow the names used, e.g. realm is test (appears as Test on Keycloak UI) if not there could be configuration problems
- Ignore the section on SAML Step 7 as it is already setup, except replace the cert ("x509cert" in main.py) with the cert generated in the Keycloak Realm that you created (see **Realm Settings -> Keys** on Keycloak admin UI)
- Ignore the section on OIDC setup
- Client specifications:
  - In addition to the steps mentioned in the setup you will need to set the following settings in the Client:
    - Clients -> "Your Client" -> Settings -> Encrypt Assertions -> ON
    - Clients -> "Your Client" -> Settings -> Sign Assertions -> ON
    - Clients -> "Your Client" -> SAML Keys -> Signing key -> import
      - Archive Format -> Certificate Pem
      - Select File -> Select your geerated sp.crt file
    - Clients -> "Your Client" -> SAML Keys -> SignEncryption Key -> import
      - Archive Format -> Certificate Pem
      - Select File -> Select your geerated sp.crt file

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
