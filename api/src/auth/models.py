import datetime

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from src.global_utils.id_generator import generate_short_id as ID_default
from src.post.models import Posts

class User(models.Model):
    """Tabela principal de usuários (equivalente a 'usuarios')"""

    id = fields.CharField(max_length=10, pk=True, default=ID_default)

    # Informações pessoais
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=150, unique=True)
    age = fields.IntField(null=True)
    password = fields.TextField()

    # Imagens de perfil
    photo = fields.TextField(default='application/src/static/uploads/1.jpg')
    banner = fields.TextField(null=True)

    # Informações da conta
    created_at = fields.DatetimeField(
        auto_now_add=True, default=datetime.datetime.now
    )
    updated_at = fields.DatetimeField(auto_now=True)
    status = fields.BooleanField(default=False)
    is_first_login = fields.BooleanField(default=True)

    # Bio e estatísticas
    bio = fields.TextField(null=True)
    followers = fields.IntField(default=0)
    following = fields.IntField(default=0)

    # Links sociais (diretos)
    github = fields.TextField(null=True)
    linkedin = fields.TextField(null=True)
    website = fields.TextField(null=True)
    temporary_code = fields.IntField(null=True, default=None)

    # Relacionamento 1:1 com UserInformation
    user_info: fields.OneToOneRelation['UserInformation']
    posts: fields.ReverseRelation['Posts']
    # Relacionamento 1:N com outras redes sociais
    other_social_networks: fields.ReverseRelation['OtherSocialNetwork']

    class Meta:
        table = 'users'

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


class UserInformation(models.Model):
    """Informações adicionais do usuário (relação 1:1)"""

    # Relacionamento 1:1 com User
    user = fields.OneToOneField(
        'models.User',
        related_name='user_info',
        on_delete=fields.CASCADE,
        pk=True,  # Mesmo ID do usuário
    )

    # Campos específicos
    username = fields.CharField(max_length=120, unique=True, null=True)
    occupation = fields.CharField(max_length=100, null=True)

    # Campos duplicados para fácil acesso
    name = fields.CharField(max_length=100, null=True)
    email = fields.CharField(max_length=150, null=True)

    class Meta:
        table = 'user_information'


class OtherSocialNetwork(models.Model):
    """Redes sociais adicionais do usuário (relação 1:N)"""

    id = fields.IntField(pk=True)

    # Relacionamento N:1 com User
    user = fields.ForeignKeyField(
        'models.User',
        related_name='other_social_networks',
        on_delete=fields.CASCADE,
    )

    # Informações da rede social
    network_name = fields.CharField(
        max_length=50
    )  # Ex: "Twitter", "Instagram"
    profile_url = fields.TextField()
    display_order = fields.IntField(default=0)  # Para ordenar na exibição

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'other_social_networks'
        ordering = ['display_order']


# Modelos Pydantic para validação
User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(
    User, name='UserIn', exclude_readonly=True
)

UserInformation_Pydantic = pydantic_model_creator(
    UserInformation, name='UserInformation'
)
UserInformationIn_Pydantic = pydantic_model_creator(
    UserInformation, name='UserInformationIn', exclude_readonly=True
)

OtherSocialNetwork_Pydantic = pydantic_model_creator(
    OtherSocialNetwork, name='OtherSocialNetwork'
)
OtherSocialNetworkIn_Pydantic = pydantic_model_creator(
    OtherSocialNetwork, name='OtherSocialNetworkIn', exclude_readonly=True
)
