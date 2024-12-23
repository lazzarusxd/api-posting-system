from passlib.context import CryptContext

criptography = CryptContext(schemes=['bcrypt'], deprecated='auto')


def generate_client_secret_hash(client_secret: str) -> str:
    return criptography.hash(client_secret)


def verify_client_secret(received_secret: str, client_secret: str) -> bool:
    return criptography.verify(received_secret, client_secret)
