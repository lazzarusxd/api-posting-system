from uuid import UUID

from fastapi import APIRouter, Depends, Path

from app.api.v1.endpoints.router_config.posting_config import Config
from app.core.deps import get_current_user
from app.models.client_auth_model import ClientAuthModel
from app.services.posting_services import PostingServices
from app.schemas.posting_schema import (
    CreatePostRequest,
    PostResponseWrapper,
    UpdatePostRequest
)

router = APIRouter()


@router.post("/new", **Config.new())
async def create_new_post(
        post_data: CreatePostRequest,
        posting_services: PostingServices = Depends(),
        _: ClientAuthModel = Depends(get_current_user)
) -> PostResponseWrapper:
    client_response = await posting_services.create_new_post(
        post_data=post_data,
        exchange="post_exchange",
        routing_key="created_rk",
        queue="created_queue"
    )

    return PostResponseWrapper(
        status_code=client_response["status_code"],
        message=client_response["message"],
        data=client_response["data"]
    )

@router.get("/info/{tracking_code}", **Config.get_info())
async def get_post_info(
        tracking_code: UUID = Path(
            title="Código de rastreamento.",
            description="Código de rastreamento (UUID) da postagem a ser retornada."
        ),
        posting_services: PostingServices = Depends(),
        _: ClientAuthModel = Depends(get_current_user)
) -> PostResponseWrapper:
    client_response = await posting_services.get_post_info(tracking_code)

    return PostResponseWrapper(
        status_code=client_response["status_code"],
        message=client_response["message"],
        data=client_response["data"]
    )

@router.put("/update/{post_id}", **Config.update())
async def update_existent_post(
        updated_post: UpdatePostRequest,
        post_id: int = Path(
            title="ID da postagem.",
            description="ID da postagem a ser atualizada."
        ),
        posting_services: PostingServices = Depends(),
        _: ClientAuthModel = Depends(get_current_user)
) -> PostResponseWrapper:
    client_response = await posting_services.update_post(
        post_id=post_id,
        updated_post=updated_post,
        exchange="post_exchange",
        routing_key="on_course_rk",
        publish_queue="on_course_queue"
    )

    return PostResponseWrapper(
        status_code=client_response["status_code"],
        message=client_response["message"],
        data=client_response["data"]
    )
