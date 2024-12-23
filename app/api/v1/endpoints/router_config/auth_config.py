from fastapi import status

from app.schemas.client_auth_schema import ClientRegisterWrapper, ClientAuthWrapper
from app.api.v1.endpoints.responses.auth_responses import Responses


class Config:

    @staticmethod
    def register():
        return {
            "response_model": ClientRegisterWrapper,
            "status_code": status.HTTP_201_CREATED,
            "summary": "Auth Register",
            "description": "Recebe os dados do cliente a ser cadastrado como utilizador da API.",
            "responses": {
                **Responses.Register.success,
                **Responses.Register.validation_errors
            }
        }

    @staticmethod
    def login():
        return {
            "response_model": ClientAuthWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Auth Login",
            "description": "Recebe os dados do cliente e retorna um token JWT e sua duração para autenticação na API.",
            "responses": {
                **Responses.Login.success,
                **Responses.Login.credential_error
            }
        }
