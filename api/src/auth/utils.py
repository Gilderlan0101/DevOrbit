# auth/utils.py

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from src.auth.config import ALGORITHM, SECRET_KEY, passwor_hash
from src.auth.schemas import UserInDB
from src.auth.models import User as db

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar se uma senha comum ex: (senha123)
    É a mesma no formato hash. basicamente uma comparação entre
    plain_password == hashed_password.

    params:
        passwor_hash: str -> Senha comum
        hashed_password: str: hash senha
    return:
        str
    """
    # TODO: Altera de -> str para oque a função retorna.
    return passwor_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Buscar hash da senha fornecida no paramentro password"""
    return passwor_hash.hash(password)


async def get_user(db, username: str):
    """get_user: Verifica se temos um usúario com o email
    fornecido no paramentro username. Se o email estive cadastrado,
    a função deve retorna os dados desse usuario."""

    user = await db.filter(email=username).first()
    if not user:
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create_access_token: Cria um token valido para o usúario."""
    try:

        to_encode = data.copy()
        if expires_delta:
            expire = (
                datetime.now(ZoneInfo('America/Sao_Paulo')) + expires_delta
            )
        else:
            expire = datetime.now(
                ZoneInfo('America/Sao_Paulo')
            ) + expires_delta(minutes=15)   # type: ignore

        to_encode.update({'exp': expire})
        encode_jwt = jwt.encode(
            to_encode, str(SECRET_KEY), algorithm=str(ALGORITHM)
        )
        return encode_jwt

    except Exception as e:
        print('auth/utils.py: create_access_token')
        return str(e)



async def authenticate_user(db, username: str, password: str):

    user = await get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
