Um JWT (JSON Web Token) **é um padrão aberto para transmitir informações de forma segura e compacta entre duas partes, como um cliente e um servidor**. Ele consiste em três partes (header, payload e signature), é assinado digitalmente para garantir a integridade e autenticidade dos dados, e é comumente usado para autenticação em APIs. Os tokens contêm "reivindicações" (claims) sobre o usuário, como sua identidade ou permissões, permitindo que o servidor verifique a identidade do usuário sem precisar consultá-lo no banco de dados a cada solicitação.

## Schemas
**SystemUser**: É uma classe responsável por guardar as informações do usuário após ele ter realizado o login/autenticação. Dentro dela podemos guardar qualquer tipo de dado que vai ser válido até o fim de vida útil da aplicação.

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class SystemUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    photo: Optional[str] = None
    status: bool = True

    model_config = {'from_attributes': True}
```

Agora criamos uma classe onde vamos guardar o id do usuário e o tempo válido para o token.
```python
class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
```
**sub**: ID do usuário
**exp**: Tempo válido do token. Normalmente 8 horas ou 7 dias. Depende do projeto.

# Passando os dados para a classe SystemUser
Para passarmos os dados do usuário para a classe precisamos buscar esses dados em algum local. Geralmente no banco de dados. Para pegar os dados temos que verificar se o usuário existe. Se sim, pegamos as informações que vamos precisar para guardar na classe.
```python

async def get_current_user(
    token: str = Depends(OAUTH2_SCHEME),
) -> SystemUser:

    token_data = DecodeToken(str(token))
    user_id = int(token_data.data.sub)

    search_target_user = await User.get_or_none(id=user_id)

    if search_target_user:
        system_user_data = SystemUser(
            id=search_target_user.id,
            username=search_target_user.username,
            email=search_target_user.email,
            photo=search_target_user.photo,
            status=search_target_user.status,
        )

        return system_user_data

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Usuário não encontrado após validação do token.',
    )
```


# Desenvolvendo um depends com validação de token da forma correta

É ideal separar todas as responsabilidades por arquivos. Vamos primeiro entender a estrutura de pastas e arquivos onde vamos desenvolver nossa verificação JWT.
```
├── config.py        <- Configuração do jwt e rotas
├── constants.py
├── dependencies.py  <- Criar dependências que serão injetadas
├── exceptions.py    <- Cria erros genéricos em constantes
├── models.py
├── router.py
├── schemas.py       <- Schemas que apenas este módulo auth/ pode usar
├── service.py
└── utils.py         <- funções úteis que todo o módulo pode usar
```

# config.py
```python
import os
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # TODO: Alterar para 8 horas


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user"}
)


```
Dentro de `config.py` podemos configurar nossas variáveis de ambiente, configurações que as rotas vão usar e afins.

# utils.py
```python

import jwt
from datetime import datetime, timedelta, timezone
from src.auth.config import (
    password_hash,
    SECRET_KEY,
    ALGORITHM,
)
from src.auth.schemas import UserInDB

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar se uma senha comum ex: (senha123)
    É a mesma no formato hash. Basicamente uma comparação entre
    plain_password == hashed_password.

    params:
        plain_password: str -> Senha comum
        hashed_password: str -> Senha hash
    return:
        bool
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Buscar hash da senha fornecida no parâmetro password"""
    return password_hash.hash(password)



async def get_user(db, username: str):
    """get_user: Verifica se temos um usuário com o email
    fornecido no parâmetro username. Se o email estiver cadastrado,
    a função deve retornar os dados desse usuário."""

    user = await db.filter(email=username).first()
    if not user:
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """ create_access_token: Cria um token válido para o usuário."""
    try:

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encode_jwt



    except Exception as e:
        print("auth/utils.py: create_access_token")
        return str(e)

```
Dentro de `utils.py` podemos criar funções que serão usadas por todo o módulo auth. Isso vai permitir criar menos códigos em outros arquivos como **`router.py`**.
Explicando o código acima:
```python
if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
```
Na primeira linha estamos verificando se um tempo válido do token foi passado para o **`expires_delta`** (no caso foi passado 30 minutos). Se foi passado, ele vai pegar o horário atual e somar mais 30 minutos. Ex: 12:30 + 30 = 13:00, ou seja, esse token vai ser válido por 30 minutos.

Agora, se o `expires_delta` não for passado, criamos um token de apenas 15 minutos. Aqui no `else` poderíamos criar uma validação melhor para que sempre seja mais de 15 minutos. Ex: poderíamos criar uma mensagem para exibir para o programador que um valor do tipo inteiro não foi passado para a função **`create_access_token`** e que o tempo padrão é 15, assim deixando o desenvolvedor avisado sobre o "problema".

**Criando e retornando um token válido:**
Agora que entendemos como criar um token com um tempo válido, vamos entender como passamos o valor datetime para criar um token.
```python
to_encode.update({"exp": expire})
encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
return encode_jwt
```
**`to_encode`**: update("exp": valor) -> Basicamente estamos adicionando o tempo válido do token em um dicionário. Ficaria algo como:
```python
token = {"exp": "2025-12-15 22:38:22.652295+00:00"}
```
Mas veja que o horário acima está em um formato diferente do brasileiro. Para gerar um token válido com horário do Brasil usamos o **`ZoneInfo`** do Python, para retornar algo como:
```
2025-12-15 20:15:51.875675-03:00
```

Implementação:
```python

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


if expires_delta:
            expire = datetime.now(ZoneInfo("America/Sao_Paulo")) + expires_delta
else:
    expire = datetime.now(ZoneInfo("America/Sao_Paulo")) + timedelta(minutes=15)
```

**Finalizando a explicação da função `create_access_token`:**
Agora que já entendemos como criar um token com tempo válido, vamos entender o que está acontecendo no final da função.
```python
encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```
- **`to_encode` (Payload):** O dicionário Python que você passa aqui (o "payload") contém os dados que você deseja armazenar no token (por exemplo, `{"sub": "123", "name": "usuario"}`).
- **`SECRET_KEY` (Chave Secreta):** Essa chave é usada para assinar digitalmente o token. Isso garante a integridade e a autenticidade do token, provando que ele não foi alterado por ninguém sem acesso à chave secreta.
- **`ALGORITHM` (Algoritmo):** Define qual método criptográfico será usado para a assinatura (comumente `"HS256"` ou `"RS256"`).

O resultado da chamada é uma _string_ longa e codificada, que representa o seu JWT final (geralmente dividido em três partes separadas por pontos: `header.payload.signature`).



## Função que verifica se as informações passadas pelo usuário realmente estão corretas

```python
async def authenticate_user(db, username: str, password: str):

    user = await get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
```

Parâmetros: db, username e password
**db**: -> Tabela onde as informações do usuário estão guardadas.
**username:** -> Email que o usuário vai passar na rota de login.
**password:** -> Senha comum que será comparada com a senha no formato hash da tabela.
```python
async def authenticate_user(db, username: str, password: str):
```


## router.py

Agora precisamos de rotas para autenticar o usuário.

```python
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import CreateAccount, Token
from src.auth.service import create_account
from src.global_utils.i_request import permitted_origin
from src.auth.utils import authenticate_user, create_access_token
from src.global_models.user import User as db
from src.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(tags=['Auth'], prefix='/auth')


@router.post('/register')
async def register_account(
    data: CreateAccount,
    origin=Depends(permitted_origin),
):

    create = await create_account(data=dict(data))
    if create:
        return create
    else:
        return create



@router.post('/login', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    user = await authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scope": " ".join(form_data.scopes)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

```
Saída
```bash
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJpYSIsInNjb3BlIjoiIiwiZXhwIjoxNzY1OTgzOTI2fQ.1V5CqNV4jGMFj15X1_fLnWQKsbKxpIcDPNWEvvdkQrE",
  "token_type": "bearer"
}
```
