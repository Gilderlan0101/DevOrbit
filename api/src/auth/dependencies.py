# auth.dependencies.py
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from src.auth.config import ALGORITHM, SECRET_KEY, auth2_scheme
from src.auth.schemas import TokenData
from src.auth.utils import get_user
from src.global_models.user import User as db


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(auth2_scheme)],
):

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope={security_scopes.scope_str}'

    else:
        authenticate_value = 'Bearer'
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': authenticate_value},
        )

    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception   # type: ignore

        scope: str = payload.get('scope', '')
        token_scopes = scope.split(' ')
        token_data = TokenData(scopes=token_scopes, username=username)

    except (InvalidTokenError, ValidationError):
        raise credentials_exception   # type: ignore

    # Buscar usúario no banco de dados com email
    # Caso não tenha um usúario com esse email,
    # a função get_user vai retorna Faslse,
    # Caso tenha um usúario a função retorna os dados desse usúario
    user = get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception   # type: ignore

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Not enough permissions',
                headers={'WWW=authenticate': authenticate_value},
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
