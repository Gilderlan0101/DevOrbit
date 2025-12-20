import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # TODO: Altera para 8 horas


passwor_hash = PasswordHash.recommended()

auth2_scheme = OAuth2PasswordBearer(
    tokenUrl='token', scopes={'me': 'Read information about the current user'}
)
