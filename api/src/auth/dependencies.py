# auth.dependencies.py
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from jose import JWTError, jwt
from pydantic import ValidationError

from src.auth.config import ALGORITHM, SECRET_KEY, oauth2_scheme
from src.auth.models import User as db
from src.auth.schemas import TokenData
from src.auth.utils import get_user

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
):


    authenticate_value = "Bearer"

    # Adicionar scopes se existirem
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope={security_scopes.scope_str}'
        print(authenticate_value)


    # Criar exceção de credenciais (agora sempre definida)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=ALGORITHM)
        username = payload.get("sub")

        if username is None:
            locals()
            #breakpoint()
            raise credentials_exception

        scope = payload.get("scope", "")
        token_scopes = scope.split()
        print(token_scopes)
        token_data = TokenData(scopes=token_scopes, username=username)

    except (JWTError, ValidationError) as e:
        raise credentials_exception

    # Buscar usuário no banco de dados
    user =  await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception

    # Verificar scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )


    return user


async def get_current_active_user(
    current_user: Annotated[db, Security(get_current_user, scopes=['me'])],
):
    if current_user.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user'
        )
    return current_user
