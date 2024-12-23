import unicodedata

from fastapi import HTTPException, status
from pytz import timezone
from pydantic import BaseModel, Field, field_validator

from app.models.client_auth_model import ClientAuthModel


class ClientRegisterRequest(BaseModel):
    nome: str = Field(
        title="Nome do cliente.",
        description="Nome do cliente a ser cadastrado.",
        examples=["JOAO DA SILVA INC"]
    )
    cpf_cnpj: str = Field(
        title="CPF/CNPJ do cliente.",
        description="CPF/CNPJ do cliente a ser cadastrado.",
        examples=["12345678912345"]
    )
    client_secret: str = Field(
        title="Senha de acesso.",
        description="Senha de acesso do cliente a ser cadastrado.",
        examples=["senha123"]
    )

    @field_validator("nome", mode="before")
    def validate_nome(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome é um campo obrigatório e não pode ser uma string vazia."
            )
        v = " ".join(v.split())
        if not all(parte.isalpha() or parte.isspace() for parte in v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O nome deve ser composto apenas por letras."
            )
        return ''.join(
            c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
        )

    @field_validator("cpf_cnpj", mode="before")
    def validate_cpf_cnpj(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF/CNPJ é um campo obrigatório e não pode ser uma string vazia."
            )
        if not v.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CPF/CNPJ deve conter apenas números."
            )
        if len(v) != 11 and len(v) != 14:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CPF/CNPJ deve conter exatamente 11 ou 14 dígitos."
            )
        return v


class ClientRegisterResponse(BaseModel):
    client_id: int = Field(
        title="ID do cliente.",
        description="ID do cliente criado.",
        examples=[1]
    )
    data_cadastro: str = Field(
        title="Data e hora dd cadastro.",
        description="Data e hora de cadastro do cliente.",
        examples=["22/12/2024 15:39:18"]
    )
    nome: str = Field(
        title="Nome do cliente.",
        description="Nome do do cliente criado.",
        examples=["JOAO DA SILVA INC"]
    )
    cpf_cnpj: str = Field(
        title="CPF/CNPJ do cliente.",
        description="CPF/CNPJ do cliente criado.",
        examples=["12345678912345"]
    )
    @classmethod
    def from_model(cls, client: ClientAuthModel) -> "ClientRegisterResponse":
        return cls(
            client_id=client.client_id,
            data_cadastro=client.data_cadastro.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S"),
            nome=client.nome,
            cpf_cnpj=client.cpf_cnpj,
        )


class ClientRegisterWrapper(BaseModel):
    status_code: int = Field(
        title="Código HTTP.",
        description="Código HTTP indicando o status da operação."
    )
    message: str = Field(
        title="Mensagem de resposta.",
        description="Mensagem que descreve o resultado da operação."
    )
    data: ClientRegisterResponse = Field(
        title="Dados do cliente.",
        description="Dados do cliente."
    )


class ClientAuthResponse(BaseModel):
    client_id: int = Field(
        title="ID do cliente.",
        description="ID do cliente criado.",
        examples=[1]
    )
    data_cadastro: str = Field(
        title="Data e hora dd cadastro.",
        description="Data e hora de cadastro do cliente.",
        examples=["22/12/2024 15:39:18"]
    )
    nome: str = Field(
        title="Nome do cliente.",
        description="Nome do do cliente criado.",
        examples=["JOAO DA SILVA INC"]
    )
    cpf_cnpj: str = Field(
        title="CPF/CNPJ do cliente.",
        description="CPF/CNPJ do cliente criado.",
        examples=["12345678912345"]
    )
    hash_token: str = Field(
        title="Token de acesso.",
        description="Token de acesso do CPF/CNPJ vinculado ao cartão."
    )
    token_expiracao: str = Field(
        title="Data de expiração do token.",
        description="Data de expiração do token do usuário."
    )

    @classmethod
    def from_model(cls, client: ClientAuthModel) -> "ClientAuthResponse":
        return cls(
            client_id=client.client_id,
            data_cadastro=client.data_cadastro.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S"),
            nome=client.nome,
            cpf_cnpj=client.cpf_cnpj,
            hash_token=client.token_hash_decrypted,
            token_expiracao=client.token_expiracao.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")
        )


class ClientAuthWrapper(BaseModel):
    status_code: int = Field(
        title="Código HTTP.",
        description="Código HTTP indicando o status da operação."
    )
    message: str = Field(
        title="Mensagem de resposta.",
        description="Mensagem que descreve o resultado da operação."
    )
    data: ClientAuthResponse = Field(
        title="Dados de acesso.",
        description="Dados de acesso a API."
    )
