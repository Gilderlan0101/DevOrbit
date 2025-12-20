# auth/service.py
from fastapi import HTTPException, status
from src.auth.utils import get_password_hash, verify_password
from src.auth.models import User, UserInformation, OtherSocialNetwork
from src.auth.schemas import (
    UserCreate,
    UserBasicResponse,
    RegisterSuccessResponse,
    LoginSuccessResponse,
)
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


async def create_account(data: UserCreate) -> RegisterSuccessResponse:
    """Cria uma conta de usuário com todas as informações relacionadas.

    Args:
        data: Dados validados do usuário

    Returns:
        RegisterSuccessResponse: Resposta padronizada de sucesso

    Raises:
        HTTPException: Em caso de erro ou email já cadastrado
    """
    try:
        # Verificar se já existe uma conta com o email fornecido
        account_exist = await User.get_or_none(email=data.email)

        if account_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='O endereço de email fornecido já está registrado.',
            )

        # Verificar se username já existe (se fornecido)
        if data.username:
            username_exist = await UserInformation.get_or_none(
                username=data.username
            )
            if username_exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='O nome de usuário fornecido já está em uso.',
                )

        # Preparar dados para a tabela User
        user_data = data.format_for_user_table()
        user_data['password'] = get_password_hash(
            password=user_data['password']
        )

        # Criar o usuário principal
        user = await User.create(**user_data)

        # Preparar dados para UserInformation
        full_name = f'{data.first_name} {data.last_name}'.strip()
        user_info_data = data.format_for_user_info_table(
            user_id=user.id, full_name=full_name
        )

        # Criar informações adicionais do usuário
        await UserInformation.create(**user_info_data)

        # Criar redes sociais adicionais (se fornecidas)
        social_networks_data = data.format_for_social_networks(user_id=user.id)
        if social_networks_data:
            for social_data in social_networks_data:
                await OtherSocialNetwork.create(**social_data)

        # Buscar usuário com relacionamentos
        user_with_relations = await User.get(id=user.id).prefetch_related(
            'user_info', 'other_social_networks'
        )

        # Converter para Pydantic
        user_response = UserBasicResponse.model_validate(user_with_relations)


        return RegisterSuccessResponse(
            user=user_response,
            # access_token=access_token,
            message='Conta criada com sucesso. Faça login para continuar.',
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao criar conta: {str(e)}',
        )
