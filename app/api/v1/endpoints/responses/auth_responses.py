class Responses:

    class Register:
        success = {
            201: {
                "description": "Cliente cadastrado com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 201,
                            "message": "Cliente cadastrado com sucesso!",
                            "data": {
                                "data_cadastro": "21/12/2024 15:04:02",
                                "client_id": 1,
                                "nome": "JOAO DA SILVA INC.",
                                "cpf_cnpj": "12345678912345"
                            }
                        }
                    }
                }
            }
        }

        validation_errors = {
            400: {
                "description": "Erros de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "Nome é um campo obrigatório e não pode ser uma string vazia.",
                                "O nome deve ser composto apenas por letras.",
                                "CPF/CNPJ é um campo obrigatório e não pode ser uma string vazia.",
                                "O CPF/CNPJ deve conter apenas números.",
                                "O CPF/CNPJ deve conter exatamente 11 ou 14 dígitos."
                            ]
                        }
                    }
                }
            }
        }

    class Login:
        success = {
            200: {
                "description": "Login efetuado com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
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
                    }
                }
            }
        }

        credential_error = {
            401: {
                "description": "Erro no login. O usuário ou senha informados são inválidos.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Dados de acesso incorretos."
                        }
                    }
                }
            }
        }
