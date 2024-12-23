from datetime import datetime

from fastapi import status, Depends, HTTPException
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import authenticate
from app.core.security import generate_client_secret_hash
from app.core.database import get_session
from app.models.client_auth_model import ClientAuthModel
from app.schemas.client_auth_schema import ClientRegisterRequest, ClientRegisterResponse, ClientAuthResponse


class ClientAuthServices:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def register(self, client: ClientRegisterRequest) -> dict:
        query = await self.db.execute(
            select(ClientAuthModel).where(
                ClientAuthModel.cpf_cnpj == client.cpf_cnpj
            )
        )
        existent_client = query.scalars().first()

        if existent_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente cadastrado com esse CPF/CNPJ.",
            )

        client = ClientAuthModel(
            data_cadastro=datetime.now(tz=timezone("America/Sao_Paulo")),
            nome=client.nome.upper(),
            cpf_cnpj=client.cpf_cnpj,
            client_secret=generate_client_secret_hash(client.client_secret)
        )

        await client.initialize()

        try:
            self.db.add(client)
            await self.db.commit()
            await self.db.refresh(client)
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao cadastrar o cliente. Tente novamente mais tarde."
            )

        return {
            "status_code": status.HTTP_201_CREATED,
            "message": "Cliente cadastrado com sucesso!",
            "data": ClientRegisterResponse.from_model(client)
        }

    @staticmethod
    async def login(client_id: int, client_secret: str) -> dict:
        client: ClientAuthModel = await authenticate(client_id=client_id, client_secret=client_secret)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Dados de acesso incorretos."
            )

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Login efetuado com sucesso!",
            "data": ClientAuthResponse.from_model(client)
        }
