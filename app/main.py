from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.configs import settings
from app.api.v1.api import router

load_dotenv()

app = FastAPI(
    title="API - Sistema de Postagens",
    description="""
    
    Esta API oferece funcionalidades para o gerenciamento de postagens, permitindo a criação de novos posts, consulta de informações de postagens e atualização do status das postagens. A API também implementa um sistema de cálculo de frete com base no volume e peso das encomendas e utiliza RabbitMQ para gerenciamento de filas de processamento, além de cache utilizando Redis para acelerar as consultas de rastreamento.
    
    Autenticação e Segurança:

    A API utiliza autenticação via tokens JWT, que são gerados durante o login com o cpf_cnpj do cliente e o client_secret. O token tem validade de 1 dia e é necessário para acessar as rotas de postagem. A API também adota criptografia e hash para garantir a segurança dos dados sensíveis, como informações sobre o cliente e as postagens.

    Endpoints disponíveis:
    
    - POST auth/register: Recebe os dados do cliente a ser cadastrado como utilizador da API.
    - POST auth: Recebe os dados do cliente e retorna um token JWT e sua duração para autenticação na API.
    - POST posting/new: Cria uma nova postagem.
    - GET posting/info/{tracking_code}: Retorna as informações de uma postagem.
    - PUT posting/update/{post_id}: Atualiza as informações de uma postagem.

    Possíveis erros:

    - 400: Erros de validação ou ao processar solicitações.
    - 401: Usuário não autenticado.
    - 404: Postagem não encontrada para o código de rastreamento ou ID informado.
    - 422: Parâmetros inválidos, como valor de frete ou peso
    - 500: Erro interno do servidor ao processar a requisição.
    """,
    version="1.0",
)
app.include_router(router, prefix=settings.API_V1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level='debug', reload=True)
