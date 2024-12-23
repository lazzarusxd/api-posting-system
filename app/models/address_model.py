from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class AddressModel(Base):
    __tablename__ = "enderecos"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    cep = Column(String, nullable=False)
    cidade = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    rua = Column(String, nullable=False)
    bairro = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    complemento = Column(String, nullable=True)

    postagens = relationship("PostModel", back_populates="endereco")
