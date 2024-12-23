from fastapi import status

from app.schemas.posting_schema import PostResponseWrapper
from app.api.v1.endpoints.responses.posting_responses import Responses


class Config:

    @staticmethod
    def new():
        return {
            "response_model": PostResponseWrapper,
            "status_code": status.HTTP_201_CREATED,
            "summary": "Create New Post",
            "description": "Cria uma nova postagem.",
            "responses": {
                **Responses.NewPost.success,
                **Responses.NewPost.validation_errors
            }
        }

    @staticmethod
    def update():
        return {
            "response_model": PostResponseWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Update Existent Post",
            "description": "Atualiza as informações de uma postagem.",
            "responses": {
                **Responses.UpdatePost.success,
                **Responses.UpdatePost.validation_error,
                **Responses.UpdatePost.invalid_id
            }
        }

    @staticmethod
    def get_info():
        return {
            "response_model": PostResponseWrapper,
            "status_code": status.HTTP_200_OK,
            "summary": "Get Existent Post",
            "description": "Retorna as informações de uma postagem.",
            "responses": {
                **Responses.GetPostInfo.success,
                **Responses.GetPostInfo.invalid_tracking_code
            }
        }
