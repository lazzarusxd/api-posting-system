import re
from pytz import timezone
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, field_validator, Field, EmailStr
from fastapi import HTTPException, status

from app.models.address_model import AddressModel
from app.models.posting_model import PostModel, PostStatus


class AddressRequest(BaseModel):
    cep: str = Field(
        title="CEP do destinatário.",
        description="CEP do endereço associado ao destinatário.",
        examples=["12345678"]
    )
    numero: str = Field(
        title="Número do endereço.",
        description="Número do endereço associado ao destinatário.",
        examples=["123"]
    )
    complemento: Optional[str] = Field(
        title="Complemento do endereço.",
        description="Complemento do endereço associado ao destinatário.",
        examples=["APTO. 10"]
    )

    @field_validator("cep", mode="before")
    def validate_cep(cls, v):
        if not v.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CEP deve conter apenas números."
            )
        if len(v) != 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CEP deve ter exatamente 8 dígitos."
            )
        return v

    @field_validator("numero", mode="before")
    def validate_numero(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O número do endereço não pode ser vazio."
            )
        if not re.match(r"^\d+$|^S/N$", v, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O número deve conter apenas dígitos ou 'S/N'."
            )
        return v


class AddressResponse(BaseModel):
    id: int = Field(
        title="ID do endereço.",
        description="ID do endereço associado a encomenda.",
        examples=[1]
    )
    cep: str = Field(
        title="CEP do destinatário.",
        description="CEP do endereço associado ao destinatário.",
        examples=["12345678"]
    )
    cidade: str = Field(
        title="Cidade do destinatário.",
        description="Cidade do endereço associado ao destinatário.",
        examples=["RIO VERDE"]
    )
    estado: str = Field(
        title="Estado do destinatário.",
        description="Estado do endereço associado ao destinatário.",
        examples=["GO"]
    )
    rua: str = Field(
        title="Rua do destinatário.",
        description="Rua do endereço associado ao destinatário.",
        examples=["RUA FELICIDADE"]
    )
    bairro: str = Field(
        title="Bairro do destinatário.",
        description="Bairro do endereço associado ao destinatário.",
        examples=["BAIRRO ALEGRIA"]
    )
    numero: str = Field(
        title="Número do endereço.",
        description="Número do endereço associado ao destinatário.",
        examples=["123"]
    )
    complemento: Optional[str] = Field(
        title="Complemento do endereço.",
        description="Complemento do endereço associado ao destinatário.",
        examples=["APTO. 10"]
    )

    @classmethod
    def from_model(cls, address: AddressModel) -> "AddressResponse":
        return cls(
            id=address.id,
            cep=address.cep,
            cidade=address.cidade.upper(),
            estado=address.estado.upper(),
            rua=address.rua.upper(),
            bairro=address.bairro.upper(),
            numero=address.numero,
            complemento=address.complemento.upper() if address.complemento else None
        )


class PostResponse(BaseModel):
    id: int = Field(
        title="ID da postagem.",
        description="ID da postagem criada.",
        examples=[1]
    )
    endereco_id: int = Field(
        title="ID do endereço.",
        description="ID do endereço vinculado a postagem.",
        examples=[1]
    )
    email: EmailStr = Field(
        title="E-mail do destinatário.",
        description="E-mail do destinatário da encomenda.",
        examples=["JOAODASILVA@EMAIL.COM"]
    )
    peso: float = Field(
        title="Peso da encomenda (em Kg).",
        description="Peso da encomenda (em Kg) vinculada a postagem.",
        examples=[6.8]
    )
    altura: float = Field(
        title="Altura da encomenda (em cm).",
        description="Altura da encomenda (em cm) vinculada a postagem.",
        examples=[10.0]
    )
    largura: float = Field(
        title="Largura da encomenda (em cm).",
        description="Largura da encomenda (em cm) vinculada a postagem.",
        examples=[5.0]
    )
    comprimento: float = Field(
        title="Comprimento da encomenda (em cm).",
        description="Comprimento da encomenda (em cm) vinculada a postagem.",
        examples=[10.0]
    )
    volume: float = Field(
        title="Volume da encomenda (em cm3).",
        description="Volume da encomenda (em cm3) vinculada a postagem.",
        examples=[500.0]
    )
    valor_frete: float = Field(
        title="Valor do frete.",
        description="Valor do frete da encomenda vinculada a postagem.",
        examples=[23.6]
    )
    data_criacao: str = Field(
        title="Data de criação.",
        description="Data e hora de criação da postagem.",
        examples=["22/12/2024 15:39:18"]
    )
    status_postagem: PostStatus = Field(
        title="Status da postagem.",
        description="Status atual da postagem.",
        examples=["CRIADO"]
    )
    data_envio: Optional[str] = Field(
        None,
        title="Data do envio da encomenda.",
        description="Data e hora em que o envio foi realizado.",
        examples=["null"]
    )
    previsao_entrega: str = Field(
        title="Previsão de entrega.",
        description="Data estimada para a entrega do pedido.",
        examples=["11/01/2025"]
    )
    data_entrega: Optional[str] = Field(
        None,
        title="Data do entrega da encomenda.",
        description="Data e hora em que a entrega foi realizada.",
        examples=["null"]
    )
    transportadora: str = Field(
        title="Transportadora escolhida.",
        description="Transportadora escolhida para efetuar a entrega.",
        examples=["CORREIOS"]
    )
    codigo_rastreamento: UUID = Field(
        title="Número de rastreamento.",
        description="Número único de rastreamento do envio.",
        examples=["d343530a-5a8a-4a07-ad51-c6458de8ffd8"]
    )
    historico_atualizacoes: dict = Field(
        title="Histórico de atualizações.",
        description="Histórico de atualização de status da encomenda.",
        examples=[{
            "22/12/2024 15:39:18": "CRIADO"
        }]
    )
    endereco: AddressResponse = Field(
        title="Endereço do destinatário.",
        description="Endereço completo do destinatário.",
        examples=[{
            "id": 1,
            "cep": "12345678",
            "cidade": "RIO VERDE",
            "estado": "GO",
            "rua": "RUA FELICIDADE",
            "bairro": "BAIRRO ALEGRIA",
            "numero": "123",
            "complemento": "APTO. 10"
        }]
    )

    @classmethod
    def from_model(cls, post: PostModel) -> "PostResponse":
        return cls(
            id=post.id,
            endereco_id=post.endereco_id,
            email=post.email,
            peso=post.peso,
            altura=post.altura,
            largura=post.largura,
            comprimento=post.comprimento,
            volume=post.volume,
            valor_frete=post.valor_frete,
            data_criacao=post.data_criacao.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S"),
            status_postagem=post.status_postagem,
            data_envio=post.data_envio.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S") if post.data_envio else None,
            previsao_entrega=post.previsao_entrega.strftime("%d/%m/%Y"),
            data_entrega=post.data_entrega.astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S") if post.data_entrega else None,
            transportadora=post.transportadora.upper(),
            codigo_rastreamento=post.codigo_rastreamento,
            historico_atualizacoes=post.historico_atualizacoes,
            endereco=AddressResponse.from_model(post.endereco)
        )


class CreatePostRequest(BaseModel):
    email: EmailStr = Field(
        title="E-mail do destinatário.",
        description="E-mail do destinatário da encomenda.",
        examples=["JOAODASILVA@EMAIL.COM"]
    )
    peso: float = Field(
        title="Peso da encomenda (em Kg).",
        description="Peso da encomenda (em Kg) a ser postada.",
        examples=[6.8]
    )
    altura: float = Field(
        title="Altura da encomenda (em cm).",
        description="Altura da encomenda (em cm) a ser postada.",
        examples=[10]
    )
    largura: float = Field(
        title="Largura da encomenda (em cm).",
        description="Largura da encomenda (em cm) a ser postada.",
        examples=[5]
    )
    comprimento: float = Field(
        title="Comprimento da encomenda (em cm).",
        description="Comprimento da encomenda (em cm) a ser postada.",
        examples=[10]
    )
    transportadora: str = Field(
        title="Transportadora escolhida.",
        description="Transportadora que efetuará a entrega.",
        examples=["CORREIOS"]
    )
    endereco: AddressRequest = Field(
        title="Endereço do destinatário.",
        description="Informar CEP, número e complemento do endereço do destinatário.",
        examples=[
            {
                "cep": "12345678",
                "numero": "123",
                "complemento": "APTO. 10"
            }
        ]
    )

    @field_validator("peso", mode="before")
    def validate_peso(cls, v):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O peso deve ser maior que 0."
            )
        return round(v, 2)

    @field_validator("altura", "largura", "comprimento", mode="before")
    def validate_dimensoes(cls, v, info):
        if v <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{info.field_name.capitalize()} deve ser maior que 0."
            )
        return round(v, 2)

    @field_validator("transportadora", mode="before")
    def validate_transportadora(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transportadora é um campo obrigatório e não pode ser vazio."
            )
        return v.upper()


class UpdatePostRequest(BaseModel):
    status_postagem: PostStatus = Field(
        title="Status da postagem.",
        description="Status atual da postagem.",
        examples=["EM_TRANSITO"]
    )

    @field_validator("status_postagem", mode="before")
    def validator_status_envio(cls, v):
        if v.upper() not in PostStatus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O status fornecido deve ser do tipo PostStatus (enum)."
            )
        return v.upper()


class PostResponseWrapper(BaseModel):
    status_code: int = Field(
        title="Código HTTP.",
        description="Código HTTP indicando o status da operação."
    )
    message: str = Field(
        title="Mensagem de resposta.",
        description="Mensagem que descreve o resultado da operação."
    )
    data: PostResponse = Field(
        title="Dados da postagem.",
        description="Dados completos da postagem."
    )
