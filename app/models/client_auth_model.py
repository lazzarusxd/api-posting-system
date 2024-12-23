from datetime import datetime, timezone, timedelta

from jose import jwt
from sqlalchemy import Column, Integer, String, DateTime, select, and_

from app.core.configs import settings
from app.core.database import Base, get_session


class ClientAuthModel(Base):
    __tablename__ = "clientes"

    client_id = Column(Integer, primary_key=True, autoincrement=True)
    data_cadastro = Column(DateTime(timezone=True), nullable=False)
    nome = Column(String, nullable=False)
    cpf_cnpj = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    hash_token = Column(String, nullable=False)
    token_expiracao = Column(DateTime(timezone=True), nullable=False)

    def __init__(self, data_cadastro, nome, cpf_cnpj, client_secret):
        super().__init__()
        self.data_cadastro = data_cadastro
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.client_secret = client_secret

    async def initialize(self):
        self.hash_token, self.token_expiracao = await self.set_or_update_token_and_token_expiration()

    async def set_or_update_token_and_token_expiration(self):
        async for db in get_session():
            query = await db.execute(
                select(ClientAuthModel).where(
                    and_(
                        ClientAuthModel.client_id == self.client_id
                    )
                )
            )
            client = query.scalars().first()

            if client:
                if client.token_expiracao < datetime.now(timezone.utc):
                    token = self._generate_token_hash(self.cpf_cnpj)
                    token_expiration = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES)

                    return token, token_expiration
                else:
                    return self.hash_token, self.token_expiracao
            else:
                token = self._generate_token_hash(self.cpf_cnpj)
                token_expiration = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES)

                return token, token_expiration

    @staticmethod
    def _generate_token_hash(cpf_cnpj: str) -> str:
        from app.core.auth import create_access_token

        token = create_access_token(cpf_cnpj)
        payload = {"token": token}
        hash_token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM,
        )
        return hash_token

    @staticmethod
    def _decrypt_token_hash(token_hash: str):
        payload = jwt.decode(
            token_hash,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("token")

    @property
    def token_hash_decrypted(self) -> str:
        return self._decrypt_token_hash(self.hash_token)
