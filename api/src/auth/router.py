from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import CreateAccount, Token
from src.auth.service import create_account
from src.global_utils.i_request import permitted_origin
from src.auth.utils import authenticate_user, create_access_token
from src.auth.models import User as db
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
    acess_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scope": " ".join(form_data.scopes)},
        expires_delta=acess_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
