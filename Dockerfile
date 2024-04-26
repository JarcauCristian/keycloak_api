FROM python:3.11-alpine

WORKDIR /app

COPY . .

ENV USERNAME = admin
ENV PASSWORD = admin
ENV CLIENT_ID = admin-cli
ENV ADD_ROLE_URL = https://keycloak.sedimark.work/auth/admin/realms/react-keycloak/users/" + userID + "/role-mappings/realm
ENV KEYCLOAK_URL = https://keycloak.sedimark.work/auth/realms/react-keycloak/protocol/openid-connect/userinfo

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python3", "main.py"]