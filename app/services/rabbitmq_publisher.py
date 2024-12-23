import json
from typing import Dict

import aio_pika
from fastapi import HTTPException, status

from app.core.configs import settings


class RabbitmqPublisher:
    def __init__(self, exchange: str, routing_key: str, queue: str):
        self.__host = settings.RABBITMQ_HOST
        self.__port = settings.RABBITMQ_PORT
        self.__username = settings.RABBITMQ_DEFAULT_USER
        self.__password = settings.RABBITMQ_DEFAULT_PASS
        self.__exchange = exchange
        self.__routing_key = routing_key
        self.__queue = queue
        self.__connection = None
        self.__channel = None

    async def __connect(self):
        try:
            url = f"amqp://{self.__username}:{self.__password}@{self.__host}:{self.__port}/"
            print(f"Connecting to RabbitMQ: {url}")

            self.__connection = await aio_pika.connect_robust(url)
            self.__channel = await self.__connection.channel()

            exchange = await self.__channel.declare_exchange(
                self.__exchange,
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            queue = await self.__channel.declare_queue(
                self.__queue,
                durable=True
            )

            await queue.bind(exchange, routing_key=self.__routing_key)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na conexão com o RabbitMQ."
            )

    async def send_message(self, body: Dict):
        await self.__connect()

        try:
            exchange = await self.__channel.get_exchange(self.__exchange)

            message_body = aio_pika.Message(
                body=json.dumps(body).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(
                message_body,
                routing_key=self.__routing_key
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no envio da mensagem. {e}"
            )
        finally:
            if self.__connection:
                await self.__connection.close()

    @staticmethod
    def publisher(exchange: str, routing_key: str, queue: str):
        if not exchange or not routing_key or not queue:
            print(exchange, routing_key, queue)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao receber as variáveis do RabbitMQ."
            )

        return RabbitmqPublisher(exchange, routing_key, queue)
