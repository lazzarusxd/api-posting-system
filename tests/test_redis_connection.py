import redis.asyncio as redis
import pytest

from app.core.configs import settings


@pytest.mark.asyncio
async def test_redis_connection():
    url_redis = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"

    if "@redis" in url_redis:
        url_redis = url_redis.replace("@redis", "@localhost")

    try:
        client = redis.Redis.from_url(url_redis)
        assert client is not None

        pong = await client.ping()
        assert pong == True

        await client.close()

    except Exception as e:
        pytest.fail(f"Erro ao conectar ao Redis: {e}")
