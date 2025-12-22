from datetime import timedelta
from os import access
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.auth.dependencies import get_current_active_user, get_current_user
from src.auth.models import User as db
from src.auth.schemas import (LoginSuccessResponse, RegisterSuccessResponse,
                              SystemUser, UserBasicResponse, UserCreate)
from src.auth.service import create_account
from src.auth.utils import authenticate_user, create_access_token
from src.global_utils.i_request import permitted_origin

router = APIRouter(tags=['Auth'], prefix='/auth')


@router.post(
    '/register',
    response_model=RegisterSuccessResponse,
    status_code=201,
    responses={
        201: {'description': 'Conta criada com sucesso'},
        409: {'description': 'Email ou username já cadastrado'},
        422: {'description': 'Erro de validação'},
        500: {'description': 'Erro interno do servidor'},
    },
)
async def register_account(data: UserCreate, origin=Depends(permitted_origin)):
    """Endpoint para registro de novos usuários.

    Realiza o cadastro completo do usuário em todas as tabelas relacionadas.

    Args:
        data: Dados validados do usuário
        origin: Validação de origem permitida

    Returns:
        RegisterSuccessResponse: Resposta padronizada com dados do usuário

    Raises:
        HTTPException: Em caso de erro na criação
    """
    return await create_account(data)


@router.post('/login', response_model=LoginSuccessResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = await authenticate_user(
        db=db, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password',
        )
    acess_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email, 'scope': ' '.join(form_data.scopes)},
        expires_delta=acess_token_expires,
    )

    user_data = UserBasicResponse(
        id=user.id,
        username=None,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=f'{user.first_name.title() } {user.last_name}',
        status=user.status,
        is_first_login=user.is_first_login,
        created_at=user.created_at,
    )

    return LoginSuccessResponse(
        success=True,
        message='Login realizado com sucesso.',
        user=user_data,
        access_token=access_token,
        refresh_token=access_token,  # TODO: Cria um refresh_token
        expires_in=30,
    )


# Rota responsavel por envia codigo de comfimação
# Para o email doo usuario
@router.post('/pull_code_email')
async def pull_code_email(
    current_user: SystemUser = Depends(get_current_user),
):

    return {'message': 'Status 200', 'User': current_user.email}
