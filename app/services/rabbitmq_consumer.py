import json
from email.message import EmailMessage
from os import environ

import aiosmtplib
import aio_pika

from app.core.configs import settings


class RabbitmqConsumer:
    def __init__(self, queue: str):
        self.__host = settings.RABBITMQ_HOST
        self.__port = settings.RABBITMQ_PORT
        self.__username = settings.RABBITMQ_DEFAULT_USER
        self.__password = settings.RABBITMQ_DEFAULT_PASS
        self.__queue = queue
        self.__connection = None
        self.__channel = None

    async def __connect(self):
        url = f"amqp://{self.__username}:{self.__password}@{self.__host}:{self.__port}/"
        print(f"Conectando ao RabbitMQ: {url}")
        self.__connection = await aio_pika.connect_robust(url)
        self.__channel = await self.__connection.channel()
        print(f"Conexão estabelecida e canal criado para a fila '{self.__queue}'.")

    async def __close_connection(self):
        if self.__connection:
            await self.__connection.close()
            print("Conexão com RabbitMQ encerrada.")

    async def consume_messages_created_queue(self, post_id: int):
        if not self.__connection or self.__connection.is_closed:
            await self.__connect()

        queue = await self.__channel.declare_queue(self.__queue, durable=True)

        async for message in queue:
            message_body = message.body.decode()
            json_msg = json.loads(message_body)

            id_from_queue = json_msg["data"]["id"]

            if id_from_queue == post_id:
                email = json_msg["data"]["email"]
                codigo_rastreamento = json_msg["data"]["codigo_rastreamento"]
                transportadora = json_msg["data"]["transportadora"]

                try:
                    await self.send_email_on_course(
                        email=email,
                        codigo_rastreamento=codigo_rastreamento,
                        transportadora=transportadora
                    )

                    await message.ack()
                    print(f"Mensagem {message.body} processada com sucesso.")
                except aiosmtplib.SMTPException as e:
                    print(f"Falha no envio do e-mail para {email} (SMTP). Erro: {e}. A mensagem não será confirmada.")
                    await message.nack(requeue=True)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar a mensagem JSON. Erro: {e}")
                    await message.nack(requeue=False)
                except Exception as e:
                    print(f"Erro inesperado. Erro: {e}. A mensagem não será confirmada.")
                    await message.nack(requeue=True)
                finally:
                    await self.__close_connection()
                    break

    async def consume_messages_on_course_queue(self, post_id: int):
        if not self.__connection or self.__connection.is_closed:
            await self.__connect()

        queue = await self.__channel.declare_queue(self.__queue, durable=True)

        async for message in queue:
            message_body = message.body.decode()
            json_msg = json.loads(message_body)

            id_from_queue = json_msg["data"]["id"]

            if id_from_queue == post_id:
                email = json_msg["data"]["email"]
                transportadora = json_msg["data"]["transportadora"]

                try:
                    await self.send_email_delivered(
                        email=email,
                        transportadora=transportadora
                    )
                    await message.ack()
                    print(f"Mensagem {message.body} processada com sucesso.")
                except aiosmtplib.SMTPException as e:
                    print(f"Falha no envio do e-mail para {email} (SMTP). Erro: {e}. A mensagem não será confirmada.")
                    await message.nack(requeue=True)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar a mensagem JSON. Erro: {e}")
                    await message.nack(requeue=False)
                except Exception as e:
                    print(f"Erro inesperado. Erro: {e}. A mensagem não será confirmada.")
                    await message.nack(requeue=True)
                finally:
                    await self.__close_connection()
                    break

    async def send_email_on_course(
            self,
            email: str,
            codigo_rastreamento: str,
            transportadora: str
    ):
        subject = "Seu pedido está em trânsito."
        content = (
            f"Olá,\n\n"
            f"Sua encomenda foi enviada pela transportadora {transportadora} com o código de rastreamento ({codigo_rastreamento})!\n"
            "Obrigado por utilizar nossos serviços.\n\n"
            "Atenciosamente,\nSistema de Postagem."
        )
        return await self.send_email(email, subject, content)

    async def send_email_delivered(
            self,
            email: str,
            transportadora: str
    ):
        subject = "Seu pedido foi entregue."
        content = (
            f"Olá,\n\n"
            f"Sua encomenda foi entregue pela transportadora {transportadora}!\n"
            "Obrigado por utilizar nossos serviços.\n\n"
            "Atenciosamente,\nSistema de Postagem."
        )
        return await self.send_email(email, subject, content)

    @staticmethod
    async def send_email(email: str, subject: str, content: str):
        print(f"Preparando para enviar o e-mail para {email} com o assunto: {subject}")
        smtp_user = environ.get("SMTP_USER")
        smtp_password = environ.get("SMTP_PASSWORD")
        smtp_host = environ.get("SMTP_HOST")
        smtp_port = int(environ.get("SMTP_PORT", 587))

        message = EmailMessage()
        message["From"] = smtp_user
        message["To"] = email
        message["Subject"] = subject
        message.set_content(content)

        max_retries = 3
        attempt = 1

        while attempt <= max_retries:
            try:
                print(f"Tentando enviar o e-mail... Tentativa {attempt}/{max_retries}")
                async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port, timeout=10) as client:
                    await client.login(smtp_user, smtp_password)
                    await client.send_message(message)
                    break
            except aiosmtplib.SMTPException as e:
                print(f"Falha ao enviar e-mail (Tentativa {attempt}/{max_retries}): {e}")
            except Exception as e:
                print(f"Ocorreu um erro inesperado (Tentativa {attempt}/{max_retries}): {e}")

            attempt += 1

        if attempt > max_retries:
            print(f"Máximo de tentativas alcançado. Falha ao enviar e-mail para {email}.")
