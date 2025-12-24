import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30   # TODO: Altera para 8 horas


passwor_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='auth/login',
    scopes={
        'user:read': 'Ler informações do usuário',
        'user:write': 'Modificar informações do usuário',
        'email:send': 'Enviar emails',
        'admin': 'Acesso administrativo completo',
    },
)


class EmailConfig:
    """Configurações de email carregadas do ambiente."""

    def __init__(self):
        self.google_app_key = str(os.getenv('GOOGLE_KEY_APP'))
        self.company_email = str(os.getenv('COMPANY_EMAIL'))
        self.app_title = str(os.getenv('APP_TITLE'))
        self._validate_config()

    def _validate_config(self) -> None:
        """Valida se as configurações necessárias estão presentes."""
        if not self.company_email or not self.google_app_key:
            raise ValueError(
                'Variáveis de ambiente de email não configuradas. '
                'Verifique COMPANY_EMAIL e GOOGLE_KEY_APP.'
            )
