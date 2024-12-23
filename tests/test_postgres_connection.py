import asyncpg
import pytest

from app.core.configs import settings


@pytest.mark.asyncio
async def test_db_connection():
    url_postgres = settings.DB_URL

    if "+asyncpg" in url_postgres:
        url_postgres = url_postgres.replace("+asyncpg", "")

    if "@postgres" in url_postgres:
        url_postgres = url_postgres.replace("@postgres", "@localhost")

    try:
        conn = await asyncpg.connect(dsn=url_postgres)
        assert conn is not None
        await conn.close()
    except Exception as e:
        pytest.fail(f"Erro ao conectar ao banco de dados: {e}")
