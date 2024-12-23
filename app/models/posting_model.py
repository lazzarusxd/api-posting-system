import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, mapped_column

from app.core.database import Base


class PostStatus(enum.Enum):
    CRIADO = "CRIADO"
    EM_TRANSITO = "EM_TRANSITO"
    ENTREGUE = "ENTREGUE"


class PostModel(Base):
    __tablename__ = "postagens"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    endereco_id = Column(Integer, ForeignKey("enderecos.id"), nullable=False)
    email = Column(String, nullable=False)
    peso = Column(Float, nullable=False)
    altura = Column(Float, nullable=False)
    largura = Column(Float, nullable=False)
    comprimento = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    valor_frete = Column(Float, nullable=False)
    data_criacao = Column(DateTime(timezone=True), nullable=False)
    status_postagem = Column(Enum(PostStatus), nullable=False)
    data_envio = Column(DateTime(timezone=True), nullable=True)
    previsao_entrega = Column(DateTime(timezone=True), nullable=False)
    data_entrega = Column(DateTime(timezone=True), nullable=True)
    transportadora = Column(String, nullable=False)
    codigo_rastreamento = Column(UUID(as_uuid=True), unique=True, nullable=False)
    historico_atualizacoes = mapped_column(JSONB, nullable=False)

    endereco = relationship("AddressModel", back_populates="postagens", lazy="joined")
