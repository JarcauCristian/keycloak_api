import os
import uvicorn
import requests
from pydantic import BaseModel
from fastapi import FastAPI, Header
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware


class AddRole(BaseModel):
    user_id: str
    role_id: str
    role_name: str


app = FastAPI(docs_url="/keycloak/docs", openapi_url="/keycloak/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/keycloak/roles")
async def get_roles(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content="Unauthorized!")

    token = authorization.split(" ")[1]
    response = requests.get(os.getenv("KEYCLOAK_URL"), headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return JSONResponse(status_code=401, content="Unauthorized!")

    data = {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "client_id": os.getenv("CLIENT_ID"),
        "grant_type": "password"
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post("https://62.72.21.79:8442/auth/realms/master/protocol/openid-connect/token",
                             data=data, headers=headers, verify=False)

    if response.status_code != 200:
        return JSONResponse("Could not get the admin token!", status_code=500)

    roles_url = "https://62.72.21.79:8442/auth/admin/realms/react-keycloak/roles"

    headers = {'Authorization': f'Bearer {response.json()["access_token"]}'}

    response = requests.get(roles_url, headers=headers, verify=False)

    if response.status_code != 200:
        return JSONResponse("Could not get the roles!", status_code=500)

    return_roles = [{"id": role["id"], "name": role["name"]} for role in response.json() if "data" in role["name"]]

    return JSONResponse(return_roles, status_code=200)


@app.post("/keycloak/role/add")
async def role_add(add_role: AddRole, authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        return JSONResponse(status_code=401, content="Unauthorized!")

    token = authorization.split(" ")[1]
    response = requests.get(os.getenv("KEYCLOAK_URL"), headers={"Authorization": f"Bearer {token}"})
    if response.status_code != 200:
        return JSONResponse(status_code=401, content="Unauthorized!")

    data = {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "client_id": os.getenv("CLIENT_ID"),
        "grant_type": "password"
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post("https://62.72.21.79:8442/auth/realms/master/protocol/openid-connect/token",
                             data=data, headers=headers, verify=False)

    if response.status_code != 200:
        return JSONResponse("Could not get the admin token!", status_code=500)

    data = [
        {"id": add_role.role_id, "name": add_role.role_name}
    ]

    headers = {
       'Content-Type': "application/json",
       'Authorization': f'Bearer {response.json()["access_token"]}'
    }

    url = f'https://62.72.21.79:8442/auth/admin/realms/react-keycloak/users/{add_role.user_id}/role-mappings/realm'

    response = requests.post(url, json=data, headers=headers, verify=False)

    if response.status_code != 204:
        return JSONResponse("Could not add role to the user!", status_code=500)

    return JSONResponse("Added role successfully!", status_code=201)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0")
