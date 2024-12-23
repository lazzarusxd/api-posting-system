from datetime import datetime, timedelta
from pytz import timezone

from jose import jwt
from sqlalchemy import select

from app.core.configs import settings
from app.core.database import get_session
from app.models.client_auth_model import ClientAuthModel
from app.core.security import verify_client_secret


async def authenticate(client_id: int, client_secret: str):
    async for db in get_session():
        query = await db.execute(
            select(ClientAuthModel).where(
                ClientAuthModel.client_id == client_id
            )
        )
        client = query.scalars().unique().one_or_none()

        if not client:
            return None
        if not verify_client_secret(client_secret, client.client_secret):
            return None

        return client


def _create_token(token_type: str, minutes_to_exp: timedelta, sub: str) -> str:
    sp = timezone("America/Sao_Paulo")
    expiration = datetime.now(tz=sp) + minutes_to_exp
    payload = {
        "type": token_type,
        "exp": expiration,
        "iat": datetime.now(tz=sp),
        "sub": str(sub)
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def create_access_token(cpf_cnpj: str) -> str:
    return _create_token(
        token_type="access_token",
        minutes_to_exp=timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES),
        sub=cpf_cnpj
    )
