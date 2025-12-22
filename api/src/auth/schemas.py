# auth/schemas.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from src.auth.models import User


class SystemUser(BaseModel):

    id: int
    username: str
    email: EmailStr
    photo: Optional[str] = None
    status: bool = True

    model_config = {'from_attributes': True}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    scopes: str
    username: str


class UserInDB(User):
    hashed_password: str


class OtherSocialNetworkCreate(BaseModel):
    """Schema para criação de redes sociais adicionais"""

    network_name: str
    profile_url: str
    display_order: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema principal para criação de conta"""

    # Informações pessoais obrigatórias
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    # Informações pessoais opcionais
    age: Optional[int] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None

    # Nome de usuário único (opcional, pode ser gerado depois)
    username: Optional[str] = None

    # Imagens de perfil
    photo: Optional[str] = None
    banner: Optional[str] = None

    # Links sociais diretos
    github: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None

    # Redes sociais adicionais
    other_social_networks: Optional[List[OtherSocialNetworkCreate]] = []

    # Status da conta
    status: Optional[bool] = True

    @field_validator('password')
    def validate_password_length(cls, v):
        if len(v) < 6:
            raise ValueError('A senha deve ter pelo menos 6 caracteres')
        return v

    @field_validator('age')
    def validate_age_range(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Idade deve estar entre 0 e 150 anos')
        return v

    @field_validator('username')
    def validate_username_format(cls, v):
        if v is not None:
            if ' ' in v:
                raise ValueError('Username não pode conter espaços')
            if len(v) < 3:
                raise ValueError('Username deve ter pelo menos 3 caracteres')
        return v

    def format_for_user_table(self) -> dict:
        """Formata os dados para a tabela User"""
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'age': self.age,
            'password': self.password,  # Será hasheado posteriormente
            'photo': self.photo or 'application/src/static/uploads/1.jpg',
            'banner': self.banner,
            'status': self.status,
            'bio': self.bio,
            'followers': 0,  # Valor padrão
            'following': 0,  # Valor padrão
            'github': self.github,
            'linkedin': self.linkedin,
            'website': self.website,
        }

    def format_for_user_info_table(self, user_id: str, full_name: str) -> dict:
        """Formata os dados para a tabela UserInformation"""
        return {
            'user_id': user_id,
            'username': self.username,
            'occupation': self.occupation,
            'name': full_name,
            'email': self.email,
        }

    def format_for_social_networks(self, user_id: str) -> list:
        """Formata os dados para a tabela OtherSocialNetwork"""
        if not self.other_social_networks:
            return []

        return [
            {
                'user_id': user_id,
                'network_name': social.network_name,
                'profile_url': social.profile_url,
                'display_order': social.display_order,
            }
            for social in self.other_social_networks
        ]


# Alias para compatibilidade
CreateAccount = UserCreate


class LoginRequest(BaseModel):
    """Schema para requisição de login"""

    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class OtherSocialNetworkResponse(BaseModel):
    """Schema de resposta para redes sociais adicionais"""

    id: int
    network_name: str
    profile_url: str
    display_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInformationResponse(BaseModel):
    """Schema de resposta para informações do usuário"""

    username: Optional[str]
    occupation: Optional[str]
    name: Optional[str]
    email: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class UserBasicResponse(BaseModel):
    """Resposta básica do usuário (para registro/login)"""

    id: str
    username: Optional[str] = None
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str] = None
    status: bool
    is_first_login: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    """Resposta completa do perfil do usuário"""

    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    age: Optional[int]

    # Imagens
    photo: Optional[str]
    banner: Optional[str]

    # Informações da conta
    created_at: datetime
    updated_at: datetime
    status: bool
    is_first_login: bool

    # Bio e estatísticas
    bio: Optional[str]
    followers: int
    following: int

    # Links sociais diretos
    github: Optional[str]
    linkedin: Optional[str]
    website: Optional[str]

    # Informações adicionais (1:1)
    user_info: Optional[UserInformationResponse]

    # Redes sociais adicionais (1:N)
    other_social_networks: List[OtherSocialNetworkResponse] = []

    # Propriedades calculadas
    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    model_config = ConfigDict(from_attributes=True)


class RegisterSuccessResponse(BaseModel):
    """Resposta de sucesso no registro"""

    success: bool = True
    message: str = 'Conta criada com sucesso'
    user: UserBasicResponse
    access_token: Optional[str] = None
    token_type: str = 'bearer'

    model_config = ConfigDict(from_attributes=True)


class LoginSuccessResponse(BaseModel):
    """Resposta de sucesso no login"""

    success: bool = True
    message: str = 'Login realizado com sucesso'
    user: UserBasicResponse
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = 'bearer'
    expires_in: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Resposta de erro padrão"""

    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ValidationErrorResponse(BaseModel):
    """Resposta para erros de validação"""

    success: bool = False
    message: str = 'Erro de validação'
    errors: List[dict]

    model_config = ConfigDict(from_attributes=True)
