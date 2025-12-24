# auth/service.py
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException, status
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from src.auth.config import EmailConfig
from src.auth.models import OtherSocialNetwork, User, UserInformation
from src.auth.schemas import (LoginSuccessResponse, RegisterSuccessResponse,
                              UserBasicResponse, UserCreate)
from src.auth.utils import (get_password_hash,
                            secret_verificatio_code_for_emails)

# Carrega variáveis de ambiente
load_dotenv()


async def create_account(data: UserCreate) -> RegisterSuccessResponse:
    """
    Cria uma conta de usuário com todas as informações relacionadas.

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
            message=f"""
                Conta criada com sucesso. Enviamos um código de confirmação para o email:
                {user_response.email}
            """,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao criar conta: {str(e)}',
        )


class EmailSender:
    """Classe responsável pelo envio de emails."""

    SMTP_SERVERS = {
        'gmail': {'host': 'smtp.gmail.com', 'port': 465},
        'outlook': {'host': 'smtp.office365.com', 'port': 465},
    }

    def __init__(self, config: EmailConfig):
        self.config = config
        self.context = ssl.create_default_context()

    def _create_message(
        self,
        receiver_email: str,
        subject: str,
        body: str,
        new_messagem: Optional[str] | None,
    ) -> MIMEText:
        """Cria o objeto da mensagem de email."""
        if new_messagem:

            message = MIMEText(new_messagem, 'plain', 'utf-8')
            message['Subject'] = subject
            message['From'] = self.config.company_email
            message['To'] = receiver_email
            return message

        else:
            message = MIMEText(body, 'plain', 'utf-8')
            message['Subject'] = subject
            message['From'] = self.config.company_email
            message['To'] = receiver_email
            return message

    def _send_with_server(
        self, server_name: str, message: MIMEText, receiver_email: str
    ) -> bool:
        """
        Tenta enviar email usando um servidor SMTP específico.

        Returns:
            bool: True se o envio foi bem-sucedido
        """
        server_config = self.SMTP_SERVERS[server_name]

        try:
            with smtplib.SMTP_SSL(
                server_config['host'],
                server_config['port'],
                context=self.context,
            ) as server:
                server.login(
                    self.config.company_email, self.config.google_app_key
                )
                server.sendmail(
                    self.config.company_email,
                    receiver_email,
                    message.as_string(),
                )
            return True
        except Exception:
            return False

    def send(
        self,
        receiver_email: str,
        subject: str,
        body: str,
        new_messagem: Optional[str] | None,
    ) -> bool:
        """
        Envia uma mensagem de email para o destinatário.

        Returns:
            bool: True se o envio for bem-sucedido
        """

        if new_messagem:
            message = self._create_message(
                receiver_email, subject, new_messagem
            )
        else:
            message = self._create_message(receiver_email, subject, body)

        # Tenta primeiro com Gmail, depois com Outlook
        if self._send_with_server('gmail', message, receiver_email):
            return True

        return self._send_with_server('outlook', message, receiver_email)


class UserCodeManager:
    """Gerencia códigos de verificação de usuários."""

    @staticmethod
    async def update_verification_code(user: User, code: str) -> bool:
        """
        Atualiza o código temporário de verificação do usuário.

        Returns:
            bool: True se o código foi atualizado com sucesso
        """
        try:
            user.temporary_code = str(code)
            await user.save()
            return True
        except Exception as e:
            print(f'Erro ao atualizar código do usuário: {e}')
            return False

    @staticmethod
    async def can_send_new_code(user: User) -> bool:
        """
        Verifica se um novo código pode ser enviado para o usuário.

        Returns:
            bool: True se pode enviar novo código
        """
        if user.temporary_code is None:
            return True

        if not user.status and user.temporary_code is not None:
            return True

        return False


class VerificationEmailService:
    """Serviço para envio de emails de verificação."""

    def __init__(self, email_sender: EmailSender, config: EmailConfig):
        self.email_sender = email_sender
        self.config = config

    def _generate_email_body(self, code: str) -> str:
        """Gera o corpo do email de verificação."""
        return f"""
            Olá!

            Ficamos felizes em ter você conosco.

            Para garantir a segurança da sua conta, por favor, utilize o código de verificação abaixo:

            CÓDIGO DE VERIFICAÇÃO: {code}

            Este código é pessoal e intransferível. Não o compartilhe com ninguém, nem mesmo com funcionários da nossa equipe.

            Se você não solicitou este código, ignore esta mensagem.
        """

    def _generate_email_subject(self) -> str:
        """Gera o assunto do email de verificação."""
        return f'[{self.config.app_title}] Código de verificação.'

    async def send_verification_code(self, target_email: str) -> bool:
        """
        Envia um código de verificação para o email do usuário.

        Returns:
            bool: True se o email foi enviado com sucesso
        """
        try:
            # Busca usuário pelo email
            user = await User.filter(email=target_email).first()
            if not user:
                print(f'Usuário com email {target_email} não encontrado.')
                return False

            # Verifica se pode enviar novo código
            if not await UserCodeManager.can_send_new_code(user):
                print('Não é possível enviar novo código para este usuário.')
                return False

            # Gera e armazena o código
            code = secret_verificatio_code_for_emails()

            if not await UserCodeManager.update_verification_code(
                user, str(code)
            ):
                print('Falha ao atualizar código do usuário.')
                return False

            # Prepara e envia o email
            subject = self._generate_email_subject()
            body = self._generate_email_body(str(code))

            return self.email_sender.send(target_email, subject, body)

        except Exception as e:
            print(f'Erro no envio de código de verificação: {e}')
            return False


async def activating_the_account_with_a_code(
    target_account: str, code: str
) -> bool:
    """
    Ativa a conta do usuário usando o código de verificação.

    Args:
        target_account: Email da conta a ser ativada
        code: Código de verificação (4 dígitos)

    Returns:
        bool: True se a conta foi ativada com sucesso

    Raises:
        HTTPException: Se o código for inválido ou muito grande
    """
    # Validação do código
    if len(code) > 4:
        raise HTTPException(
            status_code=status.HTTP_510_NOT_EXTENDED,
            detail='Código muito grande. Deve ter no máximo 4 dígitos.',
        )

    # Tenta converter para int se possível
    if code.isdigit() and len(code) == 4:
        code = int(code)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Código deve conter apenas números e ter 4 dígitos.',
        )

    try:
        target = await User.filter(email=target_account).first()

        if not target:
            return False

        pull_code = target.temporary_code

        # Verificar se o código fornecido é igual ao do banco
        if str(pull_code) == str(code):
            target.verified_account = True
            target.status = True
            await target.save()
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Código inválido. Tente novamente.',
            )

    except HTTPException:
        raise

    except (ValueError, TypeError):
        if isinstance(code, int):
            str(code)
        else:
            raise

    except Exception as e:
        print(f'Erro ao ativar conta: {e}')
        return False


# Funções de interface pública para compatibilidade com código existente


async def send_code_email(target_email: str) -> bool:
    """
    Função pública para envio de código de verificação por email.

    Mantida para compatibilidade com código existente.
    """
    try:
        config = EmailConfig()
        email_sender = EmailSender(config)
        service = VerificationEmailService(email_sender, config)

        return await service.send_verification_code(target_email)
    except ValueError as e:
        print(f'Erro de configuração: {e}')
        return False
    except Exception as e:
        print(f'Erro inesperado: {e}')
        return False


async def verify_status_account(
    code_authentication: str, target_email: str
) -> bool:
    """
    Função pública para verificação de status da conta.

    Mantida para compatibilidade com código existente.
    """
    try:
        user = await User.filter(email=target_email).first()
        if not user:
            return False

        return await UserCodeManager.update_verification_code(
            user, code_authentication
        )
    except Exception as e:
        print(f'Erro na verificação de status da conta: {e}')
        return False


def send_email_message(
    receiver_email: str,
    subject: str,
    body: str,
    new_messagem: Optional[str] | None,
) -> bool:

    """
    Função pública para envio de mensagens de email.

    Mantida para compatibilidade com código existente.
    """

    try:
        config = EmailConfig()
        email_sender = EmailSender(config)
        return email_sender.send(receiver_email, subject, body, new_messagem)
    except ValueError as e:
        print(f'Erro de configuração: {e}')
        return False
    except Exception as e:
        print(f'Erro no envio de email: {e}')
        return False
