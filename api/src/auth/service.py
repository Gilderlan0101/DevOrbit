# auth/service.py
from fastapi import HTTPException, status
from src.auth.utils import get_password_hash
from src.auth.models import User
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


async def create_account(data: dict):
    """create_account: Cria uma conta para um usúario
    params:
        data: dict | Class CreateAccount -> Schemas
    returns:
        dict = {
            "username": "User Exemplo",
            "Email": "userexemple@gmail.com",
            "status": True
        }
    """

    try:
        # Verificar se ja existe uma conta com o email fornecido.
        account_exist = await User.get_or_none(email=data.get('email'))

        if account_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='The email address provided is already registered.',
            )

        create = await User.create(
            username=data.get('username'),
            email=data.get('email'),
            password=get_password_hash(password=str(data.get('password'))),
            status=data.get('status', False),
        )

        if create:
            return {
                'username': create.username,
                'email': create.email,
                'status': 201,
            }
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error: {str(e)}',
        )
