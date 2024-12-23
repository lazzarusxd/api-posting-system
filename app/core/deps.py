from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, and_
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.configs import settings
from app.core.database import get_session
from app.models.client_auth_model import ClientAuthModel

oauth2_schema = HTTPBearer(scheme_name="BearerJWT")


async def get_current_user(
        db: AsyncSession = Depends(get_session),
        token: HTTPAuthorizationCredentials = Depends(oauth2_schema)
) -> ClientAuthModel:
    credential_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        cpf_cnpj = payload.get("sub")

        if cpf_cnpj is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    query = await db.execute(
        select(ClientAuthModel).where(
            and_(ClientAuthModel.cpf_cnpj == cpf_cnpj)
        )
    )
    usuario = query.scalars().first()

    if usuario is None:
        raise credential_exception

    return usuario
