from fastapi import APIRouter, Depends, Query

from app.services.client_auth_services import ClientAuthServices
from app.api.v1.endpoints.router_config.auth_config import Config
from app.schemas.client_auth_schema import (
    ClientRegisterRequest,
    ClientRegisterWrapper,
    ClientAuthWrapper
)

router = APIRouter()


@router.post("/register", **Config.register())
async def register(
        client_data: ClientRegisterRequest,
        client_auth_services: ClientAuthServices = Depends()
) -> ClientRegisterWrapper:
    client_response = await client_auth_services.register(client_data)

    return ClientRegisterWrapper(
        status_code=client_response["status_code"],
        message=client_response["message"],
        data=client_response["data"]
    )


@router.post("", **Config.login())
async def login(
        client_id: int = Query(
            title="ID do cliente.",
            description="ID do cliente a ser autenticado."
        ),
        client_secret: str = Query(
            title="Secret do cliente.",
            description="Secret do cliente a ser autenticado."
        ),
        client_auth_services: ClientAuthServices = Depends()
) -> ClientAuthWrapper:
    client_response = await client_auth_services.login(client_id, client_secret)

    return ClientAuthWrapper(
        status_code=client_response["status_code"],
        message=client_response["message"],
        data=client_response["data"]
    )
