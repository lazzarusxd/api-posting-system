import aio_pika
import pytest

from app.core.configs import settings


@pytest.mark.asyncio
async def test_rabbitmq_connection():
    url_rabbitmq = f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"

    if "@rabbitmq" in url_rabbitmq:
        url_rabbitmq = url_rabbitmq.replace("@rabbitmq", "@localhost")

    try:
        connection = await aio_pika.connect_robust(url_rabbitmq)
        assert connection is not None

        async with connection:
            channel = await connection.channel()
            assert channel is not None

        await connection.close()
    except Exception as e:
        pytest.fail(f"Erro ao conectar ao RabbitMQ: {e}")
