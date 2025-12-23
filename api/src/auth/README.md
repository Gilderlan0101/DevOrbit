```markdown
# JWT (JSON Web Token) - Guia Completo com FastAPI

## O que é JWT?
Um **JWT (JSON Web Token)** é um padrão aberto (RFC 7519) para transmitir informações de forma segura e compacta entre duas partes, como um cliente e um servidor. Ele consiste em três partes (header, payload e signature) e é comumente usado para autenticação em APIs RESTful.

## Estrutura do Token
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  # Header (codificado)
eyJzdWIiOiJqb2FvQGV4YW1wbGUuY29tIiwic2NvcGUiOiJlbWFpbDpzZW5kIHVzZXI6cmVhZCIsImV4cCI6MTc2NjUwOTI3NH0.  # Payload (codificado)
N2q_Mj7sGvGEyn4Tpb8sd2PQ_TBFTqip3YgwGEM6Meg  # Assinatura
```

## Estrutura do Projeto
```
src/auth/
├── config.py        # Configurações do JWT e OAuth2
├── dependencies.py  # Dependências para injeção (get_current_user, etc.)
├── exceptions.py    # Exceções personalizadas
├── models.py        # Modelos do banco de dados
├── router.py        # Rotas da API
├── schemas.py       # Schemas Pydantic
├── service.py       # Lógica de negócio
└── utils.py         # Funções utilitárias
```

## Configuração (config.py)
```python
import os
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente (definir no .env)
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-min-32-caracteres")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Hash de senhas
password_hash = PasswordHash.recommended()

# Esquema OAuth2 com scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={
        "user:read": "Ler informações do usuário",
        "user:write": "Modificar informações do usuário",
        "email:send": "Enviar emails",
        "admin": "Acesso administrativo completo",
    }
)
```

## Schemas (schemas.py)
```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

class SystemUser(BaseModel):
    """Schema para informações básicas do usuário autenticado"""
    id: str
    username: Optional[str] = None
    email: EmailStr
    photo: Optional[str] = None
    status: bool = True

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    """Resposta do login"""
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

class TokenData(BaseModel):
    """Dados extraídos do token JWT"""
    username: str
    scopes: List[str] = []

class UserCreate(BaseModel):
    """Schema para criação de conta"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    age: Optional[int] = None
    occupation: Optional[str] = None

    @field_validator('password')
    def validate_password_length(cls, v):
        if len(v) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres')
        return v
```

## Utilitários (utils.py)
```python
import jwt
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

from src.auth.config import SECRET_KEY, ALGORITHM, password_hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return password_hash.hash(password)

async def get_user(db, username: str):
    """Busca usuário por email (username é o email)"""
    user = await db.filter(email=username).first()
    if not user or not user.status:
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT com tempo de expiração"""
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(ZoneInfo('America/Sao_Paulo')) + expires_delta
        else:
            expire = datetime.now(ZoneInfo('America/Sao_Paulo')) + timedelta(minutes=15)

        # IMPORTANTE: Definir scopes adequados para cada tipo de usuário
        if "scope" not in to_encode:
            # Scopes padrão - ajustar conforme necessidade
            to_encode.update({
                "scope": "email:send user:read user:write"
            })

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    except Exception as e:
        print(f'Erro em create_access_token: {e}')
        raise

async def authenticate_user(db, username: str, password: str):
    """Autentica usuário com email e senha"""
    user = await get_user(db=db, username=username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def secret_verification_code_for_emails() -> int:
    """Gera código de verificação de 4 dígitos"""
    return random.randint(1000, 9999)
```

## Dependências (dependencies.py)
```python
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jose import JWTError
from pydantic import ValidationError

from src.auth.config import ALGORITHM, SECRET_KEY, oauth2_scheme
from src.auth.models import User as db
from src.auth.schemas import TokenData, SystemUser
from src.auth.utils import get_user

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> SystemUser:
    """Dependência principal para autenticação com scopes"""

    # Configurar valor do header WWW-Authenticate
    authenticate_value = "Bearer"
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope={security_scopes.scope_str}'

    # Exceção padrão para credenciais inválidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        # DECODIFICAR TOKEN - ATENÇÃO: algoritmo deve ser string simples
        algorithm_to_use = ALGORITHM if ALGORITHM else "HS256"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm_to_use])

        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Extrair scopes do token (campo "scope" como string)
        scope = payload.get("scope", "")
        token_scopes = scope.split()
        token_data = TokenData(scopes=token_scopes, username=username)

    except (JWTError, ValidationError):
        raise credentials_exception

    # Buscar usuário no banco (username aqui é o email)
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    # Verificar se token tem todos os scopes requeridos
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Missing scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    # Converter para SystemUser
    return SystemUser(
        id=str(user.id),
        username=user.username,
        email=user.email,
        photo=user.photo,
        status=user.status
    )

async def get_current_active_user(
    current_user: Annotated[SystemUser, Security(get_current_user, scopes=["me"])],
):
    """Dependência que verifica se usuário está ativo"""
    if not current_user.status:  # status=False significa inativo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user'
        )
    return current_user
```

## Rotas (router.py)
```python
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import CreateAccount, LoginSuccessResponse, UserBasicResponse
from src.auth.service import create_account
from src.global_utils.i_request import permitted_origin
from src.auth.utils import authenticate_user, create_access_token
from src.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.dependencies import get_current_user
from src.auth.schemas import SystemUser

router = APIRouter(tags=['Auth'], prefix='/auth')

@router.post('/register', response_model=dict)
async def register_account(
    data: CreateAccount,
    origin: bool = Depends(permitted_origin),
):
    """Registra nova conta de usuário"""
    result = await create_account(data=dict(data))
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Erro no registro")
        )
    return result

@router.post('/login', response_model=LoginSuccessResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Autentica usuário e retorna token JWT"""

    user = await authenticate_user(
        db=db,  # Sua instância do banco
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    # IMPORTANTE: Definir scopes adequados
    user_scopes = ["email:send", "user:read", "user:write"]

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "scope": " ".join(user_scopes)},
        expires_delta=access_token_expires,
    )

    user_data = UserBasicResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f'{user.first_name} {user.last_name}',
        status=user.status,
        is_first_login=user.is_first_login,
        created_at=user.created_at,
    )

    return LoginSuccessResponse(
        success=True,
        message="Login realizado com sucesso",
        user=user_data,
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # em segundos
    )

@router.post('/pull_code_email')
async def pull_code_email(
    current_user: SystemUser = Security(get_current_user, scopes=["email:send"]),
    origin: bool = Depends(permitted_origin),
):
    """Rota protegida que requer scope específico"""
    return {
        'message': 'Código enviado com sucesso',
        'User': current_user.email
    }
```

## Uso em Outras Rotas
```python
# Exemplo em outro módulo (posts, por exemplo)
from fastapi import APIRouter, Depends, Security
from src.auth.dependencies import get_current_user
from src.auth.schemas import SystemUser

router = APIRouter(tags=['Posts'], prefix='/posts')

@router.post('/create')
async def create_post(
    data: dict,
    current_user: SystemUser = Security(get_current_user, scopes=["user:write"]),
):
    """Cria post - requer scope user:write"""
    # Lógica para criar post
    return {"message": "Post criado", "author": current_user.email}

@router.get('/my-posts')
async def get_my_posts(
    current_user: SystemUser = Security(get_current_user, scopes=["user:read"]),
):
    """Lista posts do usuário - requer scope user:read"""
    # Lógica para buscar posts
    return {"posts": [], "user": current_user.email}
```

## Problemas Comuns e Soluções

### 1. **401 Unauthorized - "Could not validate credentials"**
**Causas:**
- Token expirado
- Assinatura inválida (SECRET_KEY errada)
- Algoritmo incorreto (verificar ALGORITHM no .env)

**Solução:**
```python
# config.py - garantir que ALGORITHM seja string simples
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # "HS256", não '"HS256"'
```

### 2. **403 Forbidden - "Not enough permissions"**
**Causa:** Token não tem o scope requerido pela rota.

**Solução:** Adicionar scope ao token:
```python
# utils.py - em create_access_token
to_encode.update({
    "scope": "email:send user:read user:write"  # Incluir todos os scopes necessários
})
```

### 3. **Erro no decode: "alg value is not allowed"**
**Causa:** `str(ALGORITHM)` adiciona aspas extras.

**Solução:**
```python
# dependencies.py - em get_current_user
# ERRADO:
payload = jwt.decode(token, SECRET_KEY, algorithms=[str(ALGORITHM)])

# CORRETO:
algorithm_to_use = ALGORITHM if ALGORITHM else "HS256"
payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm_to_use])
```

### 4. **Usuário não encontrado após login**
**Causa:** Campo `status=False` por padrão (espera validação por email).

**Solução:** Alterar `status` para `True` após validação ou ajustar lógica:
```python
# utils.py - em get_user
async def get_user(db, username: str):
    user = await db.filter(email=username).first()
    # Remover verificação de status se quiser permitir login antes da validação
    if not user:  # ou if not user or not user.status:
        return None
    return user
```

## Variáveis de Ambiente (.env)
```env
SECRET_KEY=sua-chave-secreta-min-32-caracteres-aqui
ALGORITHM=HS256
DATABASE_URL=sqlite:///./community.db
```

## Testando com cURL
```bash
# 1. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=joao@exemplo.com&password=senha123"

# 2. Usar token em rota protegida
curl -X POST "http://localhost:8000/auth/pull_code_email" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "accept: application/json"

# 3. Criar post (outro módulo)
curl -X POST "http://localhost:8000/posts/create" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"title": "Meu post", "content": "Conteúdo"}'
```

## Fluxo Completo
1. **Registro** → `/auth/register` (cria conta com `status=False`)
2. **Validação por email** → usuário recebe código, valida conta (`status=True`)
3. **Login** → `/auth/login` (gera token com scopes)
4. **Acesso a rotas protegidas** → token no header `Authorization: Bearer <token>`
5. **Verificação automática** → `get_current_user` valida token e scopes

## Boas Práticas
1. **Scopes granulares:** Use scopes específicos (`user:read`, `user:write`)
2. **Tokens de curta duração:** 15-30 minutos para access_token
3. **Refresh tokens:** Implemente para renovação sem novo login
4. **HTTPS sempre:** JWT deve ser transmitido apenas por HTTPS
5. **Logout server-side:** Para revogação imediata, use blacklist de tokens

Este sistema implementa autenticação JWT robusta com FastAPI, incluindo scopes para controle de permissões e tratamento de erros apropriado.
```
