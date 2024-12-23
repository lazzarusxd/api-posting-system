class Responses:

    class NewPost:
        success = {
            201: {
                "description": "Postagem criada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 201,
                            "message": "Postagem criada com sucesso.",
                            "data": {
                                "id": 1,
                                "endereco_id": 1,
                                "email": "JOAODASILVA@EMAIL.COM",
                                "peso": 6.8,
                                "altura": 10.0,
                                "largura": 5.0,
                                "comprimento": 10.0,
                                "volume": 500.0,
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
                    }
                }
            }
        }

        validation_errors = {
            400: {
                "description": "Erro de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O CEP deve conter apenas números.",
                                "O CEP deve ter exatamente 8 dígitos.",
                                "CEP inválido ou não encontrado.",
                                "O número do endereço não pode ser vazio.",
                                "O número deve conter apenas dígitos ou 'S/N'.",
                                "O peso deve ser maior que 0.",
                                "Altura deve ser maior que 0.",
                                "Largura deve ser maior que 0.",
                                "Comprimento deve ser maior que 0.",
                                "Transportadora é um campo obrigatório e não pode ser vazio."
                            ]
                        }
                    }
                }
            }
        }

    class GetPostInfo:
        success = {
            200: {
                "description": "Postagem retornada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 200,
                            "message": "Postagem retornada com sucesso.",
                            "data": {
                                "id": 1,
                                "endereco_id": 1,
                                "email": "JOAODASILVA@EMAIL.COM",
                                "peso": 6.8,
                                "altura": 10.0,
                                "largura": 5.0,
                                "comprimento": 10.0,
                                "volume": 500.0,
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
                    }
                }
            }
        }

        invalid_tracking_code = {
            404: {
                "description": "Erro no path. O código de rastreamento informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Não foram encontradas postagens com código de rastreamento informado."
                        }
                    }
                }
            }
        }

    class UpdatePost:
        success = {
            200: {
                "description": "Postagem atualizada com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 200,
                            "message": "Dados atualizados com sucesso.",
                            "data": {
                                "id": 1,
                                "endereco_id": 1,
                                "email": "JOAODASILVA@EMAIL.COM",
                                "peso": 6.8,
                                "altura": 10.0,
                                "largura": 5.0,
                                "comprimento": 10.0,
                                "volume": 500.0,
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
                    }
                }
            }
        }

        validation_error = {
            400: {
                "description": "Erros de validação (campos vazios, nulos ou inválidos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O status fornecido deve ser do tipo PostStatus (enum).",
                                "Requisição inválida. Não é possível alterar o status de uma postagem já criada para o status CRIADO.",
                                "Requisição inválida. A postagem já se encontra com o status EM_TRANSITO.",
                                "Requisição inválida. A postagem já se encontra com o status ENTREGUE.",
                                "Requisição inválida. Essa postagem já foi entregue ao destinatário.",
                                "Requisição inválida. Essa postagem ainda não passou pelo processo de entrega."
                            ]
                        }
                    }
                }
            }
        }

        invalid_id = {
            404: {
                "description": "Erro no path. Não foram encontradas postagens com o ID informado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Não foram encontradas postagens com o ID informado."
                        }
                    }
                }
            }
        }
