# API - Posting System

## Descrição

Esta API oferece funcionalidades para o gerenciamento de postagens, permitindo a criação de novos posts, consulta de informações de postagens e atualização do status das postagens. A API também implementa um sistema de cálculo de frete com base no volume e peso das encomendas e utiliza RabbitMQ para gerenciamento de filas de processamento, além de cache utilizando Redis para acelerar as consultas de rastreamento.

## Funcionalidades

- **Cadastro de Cliente (auth/signup):** Permite que um novo cliente se cadastre no sistema, inserindo seu nome, CPF/CNPJ e client_secret. Esses dados são salvos no banco de dados para gerar um novo usuário que poderá utilizar as funcionalidades da API de postagem.

- **Login (auth):** Permite que o cliente se autentique na API utilizando client_id e seu client_secret como query parameter. A rota retorna um token JWT com validade de 1 dia, contendo o CPF/CNPJ do cliente como payload. Esse token é utilizado para autenticação nas rotas de postagem.

- **Criação de Postagem (posting/new):** Cria um novo post no sistema com o status "CRIADO" e salva as informações na fila RabbitMQ "created_queue". A postagem também calcula o valor do frete de acordo com o volume e o peso do pacote. O cálculo do frete considera:
  - Frete mínimo de 20 reais.
  - Para pacotes com volume superior a 3000 cm³, cobra-se 1 real por cada 500 cm³ excedentes. 
  - Para pacotes com peso superior a 5 kg, cobra-se R$ 2,00 por cada kg excedente.

- **Consultar Informações de Postagem (posting/info/{tracking_number}):** Retorna as informações de uma postagem através do código de rastreamento fornecido. Esta rota utiliza o Redis para cachear as informações da postagem por 5 minutos, a fim de otimizar o desempenho e reduzir a carga no banco de dados.

- **Atualização de Status da Postagem (posting/update/{post_id}):** Permite atualizar o status de uma postagem identificada pelo post_id no path. O status pode ser alterado para "EM_TRANSITO" ou "ENTREGUE".
     - Quando o status for alterado para "EM_TRANSITO", consome-se a mensagem da fila "created_queue", envia-se um e-mail ao destinatário informando que a encomenda está em trânsito e salva-se uma nova mensagem na fila "on_course_queue".
     - Quando o status for alterado para "ENTREGUE", consome-se a mensagem da fila "on_course_queue", envia-se um e-mail ao destinatário informando que a encomenda foi entregue com sucesso.
     - Em ambas as atualizações, as informações são armazenadas no Redis com o código de rastreamento como chave e o schema de resposta de post como valor, garantindo que o status da postagem seja atualizado no cache.
     - Um histórico de atualização é criado, com a data e o horário da atualização, e o status alterado, além de preencher os campos data_envio (para "EM_TRANSITO") e data_entrega (para "ENTREGUE").

## Segurança e Autenticação

A API utiliza autenticação via tokens JWT, que são gerados durante o login efetuado com o client_id e o client_secret. O token tem validade de 1 dia e é necessário para acessar as rotas de postagem. A API também adota criptografia e hash para garantir a segurança dos dados sensíveis, como informações sobre o cliente e as postagens.

## Estrutura do Projeto

```plaintext
api-posting-system/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── responses/
│   │   │   │   │   ├── auth_responses.py
│   │   │   │   │   └── posting_responses.py
│   │   │   │   ├── router_config/
│   │   │   │   │   ├── auth_config.py
│   │   │   │   │   └── posting_config.py
│   │   │   │   ├── auth.py
│   │   │   │   └── posting.py
│   │   │   └── api.py
│   ├── core/
│   │   ├── auth.py
│   │   ├── configs.py
│   │   ├── database.py
│   │   ├── deps.py
│   │   └── security.py
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── README
│   │   └── script.py.mako
│   ├── models/
│   │   ├── address_model.py
│   │   ├── client_auth_model.py
│   │   └── posting_model.py
│   ├── schemas/
│   │   ├── client_auth_schema.py
│   │   └── posting_schema.py
│   ├── services/
│   │   ├── client_auth_services.py
│   │   ├── posting_services.py
│   │   ├── rabbitmq_consumer.py
│   │   └── rabbitmq_publisher.py
│   ├── alembic.ini
│   └── main.py
├── tests/
│   ├── test_postgres_connection.py
│   ├── test_rabbitmq_connection.py
│   └── test_redis_connection.py
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
└── pyproject.toml
```

## Como Usar

1- Clone este repositório:
```bash
git clone https://github.com/lazzarusxd/api-posting-system.git
```

2- Navegue até o diretório do projeto:
```bash
cd api-posting-system
```

3- Crie seu ambiente de desenvolvimento e instale as dependências usando Poetry:
```bash
poetry install
```

4- Execute seu ambiente de desenvolvimento com as dependências usando Poetry:
```bash
poetry shell
```

5- Configure o interpretador Python na sua IDE:
- Caso seu ambiente de desenvolvimento tenha sido criado no WSL, selecione-o e escolha a opção "System Interpreter".
  
- Navegue até o diretório retornado no terminal após a execução do comando do Passo 5.
  
- Procure o executável do Python dentro do ambiente virtual.

6- Crie e execute os containers Docker necessários:
```bash
docker-compose up --build
```

7- Crie uma conexão no banco de dados:
- Solicite ou crie o arquivo ".env" com as informações:
    ```bash
    POSTGRES_USER=seu_user
    POSTGRES_PASSWORD=sua_senha
    POSTGRES_DB=posting
    DB_URL=postgresql+asyncpg://seu_user:sua_senha@postgres:5432/posting
    PGADMIN_DEFAULT_EMAIL=seu_email
    PGADMIN_DEFAULT_PASSWORD=sua_senha
    ```

- Acesse o pgAdmin, endereço padrão (localhost:5050) e faça login com os seus dados salvos no ".env".
  
- Clique com o botão direito do mouse em Servers, selecione Register e Server:
  - Em General, preencha name de acordo com o nome que deseja dar a conexão.
  - Em Connection, insira em "Host name/address" e "port" as informações contidas após o @ em seu DB_URL, no exemplo, host (postgres) e port (5432), em "Maintenance database" insira a informação do seu POSTGRES_DB, em "username" (POSTGRES_USER) em "password" (POSTGRES_PASSWORD).
  - Após concluído, clique em "Save" e sua conexão terá sido criada.

8- Crie a tabela no banco de dados usando Alembic:
```bash
docker exec -it api-posting-system-app-1 poetry run alembic upgrade head
```

9- Realize as requisições desejadas conforme o próximo tópico (Endpoints):
   - Solicite o arquivo original ".env" ou configure-o conforme suas necessidades.
     
   - Verifique as portas corretas dos serviços utilizando o aplicativo Docker Desktop ou o comando:

      ```bash
      docker ps
      ```

## Endpoints

### **Cadastro de Cliente**:

- ***Rota***: POST auth/register
- ***Descrição***: Recebe os dados do cliente a ser cadastrado como utilizador da API.

**Exemplo de entrada:**

```plaintext
{
  "nome": "JOAO DA SILVA INC",
  "cpf_cnpj": "12345678912345",
  "client_secret": "senha123"
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 201,
  "message": "Cliente cadastrado com sucesso!",
  "data": {
    "data_cadastro": "21/12/2024 15:04:02",
    "client_id": 1,
    "nome": "JOAO DA SILVA INC.",
    "cpf_cnpj": "12345678912345"
  }
}
```

### **Autenticação de Cliente**:

- ***Rota***: POST auth
- ***Descrição***: Recebe os dados do cliente e retorna um token JWT e sua duração para autenticação na API.

**Exemplo de entrada:**

```plaintext
URL http://localhost:8000/api/v1/auth?client_id=1&client_secret=senha123
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 200,
  "message": "Login efetuado com sucesso!",
  "data": {
    "data_cadastro": "21/12/2024 15:04:02",
    "client_id": 1,
    "nome": "JOAO DA SILVA INC.",
    "cpf_cnpj": "12345678912345",
    "hash_token": "eyciOiJIUzI1NiIsIn.eyJ0eXBzX3Rva2Vu0LCJpYXQiTI3M.iMH9FeGcvLM9kWgmbGVUM",
    "token_expiracao": "22/12/2024 15:06:02"
  }
}
```

### **Criar Postagem (requer autenticação - Bearer JWT)**:

- ***Rota***: POST posting/new
- ***Descrição***: Cria uma nova postagem.

**Exemplo de entrada:**

```plaintext
{
  "email": "JOAODASILVA@EMAIL.COM",
  "peso": 6.8,
  "altura": 10,
  "largura": 5,
  "comprimento": 10,
  "transportadora": "CORREIOS",
  "endereco": {
    "cep": "12345678",
    "complemento": "APTO. 10",
    "numero": "123"
  }
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 201,
  "message": "Postagem criada com sucesso.",
  "data": {
    "id": 1,
    "endereco_id": 1,
    "email": "JOAODASILVA@EMAIL.COM",
    "peso": 6.8,
    "altura": 10,
    "largura": 5,
    "comprimento": 10,
    "volume": 500,
    "valor_frete": 23.6,
    "data_criacao": "22/12/2024 15:39:18",
    "status_postagem": "CRIADO",
    "data_envio": "null",
    "previsao_entrega": "11/01/2025",
    "data_entrega": "null",
    "transportadora": "CORREIOS",
    "codigo_rastreamento": "d343530a-5a8a-4a07-ad51-c6458de8ffd8",
    "historico_atualizacoes": {
      "22/12/2024 15:39:18": "CRIADO"
    },
    "endereco": {
      "id": 1,
      "cep": "12345678",
      "cidade": "RIO VERDE",
      "estado": "GO",
      "rua": "RUA FELICIDADE",
      "bairro": "BAIRRO ALEGRIA",
      "numero": "123",
      "complemento": "APTO. 10"
    }
  }
}
```

### **Informações da Postagem (requer autenticação - Bearer JWT)**:

- ***Rota***: GET posting/info/{tracking_code}
- ***Descrição***: Retorna as informações de uma postagem.

**Exemplo de entrada:**

```plaintext
http://localhost:8000/api/v1/posting/info/d343530a-5a8a-4a07-ad51-c6458de8ffd8
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 200,
  "message": "Postagem retornada com sucesso.",
  "data": {
    "id": 1,
    "endereco_id": 1,
    "email": "JOAODASILVA@EMAIL.COM",
    "peso": 6.8,
    "altura": 10,
    "largura": 5,
    "comprimento": 10,
    "volume": 500,
    "valor_frete": 23.6,
    "data_criacao": "22/12/2024 15:39:18",
    "status_postagem": "CRIADO",
    "data_envio": "null",
    "previsao_entrega": "11/01/2025",
    "data_entrega": "null",
    "transportadora": "CORREIOS",
    "codigo_rastreamento": "d343530a-5a8a-4a07-ad51-c6458de8ffd8",
    "historico_atualizacoes": {
      "22/12/2024 15:39:18": "CRIADO"
    },
    "endereco": {
      "id": 1,
      "cep": "12345678",
      "cidade": "RIO VERDE",
      "estado": "GO",
      "rua": "RUA FELICIDADE",
      "bairro": "BAIRRO ALEGRIA",
      "numero": "123",
      "complemento": "APTO. 10"
    }
  }
}
```

### **Atualiza Status da Postagem (requer autenticação - Bearer JWT)**:

- ***Rota***: PUT posting/update/{post_id}
- ***Descrição***: Atualiza as informações de uma postagem.

**Exemplo de entrada:**

```plaintext
URL http://localhost:8000/api/v1/posting/update/1

{
  "status_postagem": "EM_TRANSITO"
}
```

**Exemplo de resposta bem sucedida:**

```plaintext
{
  "status_code": 200,
  "message": "Dados atualizados com sucesso.",
  "data": {
    "id": 1,
    "endereco_id": 1,
    "email": "JOAODASILVA@EMAIL.COM",
    "peso": 6.8,
    "altura": 10,
    "largura": 5,
    "comprimento": 10,
    "volume": 500,
    "valor_frete": 23.6,
    "data_criacao": "22/12/2024 17:23:45",
    "status_postagem": "EM_TRANSITO",
    "data_envio": "22/12/2024 17:23:59",
    "previsao_entrega": "11/01/2025",
    "data_entrega": "22/12/2024 17:24:26",
    "transportadora": "CORREIOS",
    "codigo_rastreamento": "d343530a-5a8a-4a07-ad51-c6458de8ffd8",
    "historico_atualizacoes": {
      "22/12/2024 17:23:45": "CRIADO",
      "22/12/2024 17:23:59": "EM_TRANSITO"
    },
    "endereco": {
      "id": 1,
      "cep": "12345678",
      "cidade": "RIO VERDE",
      "estado": "GO",
      "rua": "RUA FELICIDADE",
      "bairro": "BAIRRO ALEGRIA",
      "numero": "123",
      "complemento": "APTO. 10"
    }
  }
}
```

### **Possíveis Erros**:

- ***400***: Erros de validação ou ao processar solicitações.
- ***401***: Usuário não autenticado.
- ***404***: Postagem não encontrada para o código de rastreamento ou ID informado.
- ***422***: Parâmetros inválidos, como valor de frete ou peso.
- ***500***: Erro interno do servidor ao processar a requisição.



## Contato:

João Lázaro - joaolazarofera@gmail.com

Link do projeto - https://github.com/lazzarusxd/api-posting-system
