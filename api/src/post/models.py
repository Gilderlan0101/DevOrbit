# src/post/models.py
from datetime import datetime
from zoneinfo import ZoneInfo

from tortoise import fields, models
from tortoise.signals import pre_save

from src.global_utils.id_generator import generate_short_id as ID_default


class Posts(models.Model):
    """Tabela de posts dos usuários"""

    # ID personalizado
    id = fields.CharField(max_length=10, pk=True, default=ID_default)

    user = fields.ForeignKeyField(
        'models.User',  # Referência ao modelo User
        related_name='posts',  # user.posts retorna posts do usuário
        on_delete=fields.CASCADE,  # Deleta posts se usuário for deletado
        null=False,
    )

    # Informações do post
    autho_nickname = fields.CharField(max_length=255, null=True)
    title = fields.CharField(max_length=250)
    content = fields.TextField()
    quantity_likes = fields.IntField(default=0)
    photo = fields.TextField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Campo para categorias/tags (opcional)
    category = fields.CharField(max_length=100, null=True)
    tags = fields.JSONField(null=True)  # Para armazenar lista de tags

    # Status do post
    is_published = fields.BooleanField(default=True)
    is_deleted = fields.BooleanField(default=False)

    @pre_save
    async def populate_author_info(self):
        """Popula automaticamente os dados do autor antes de salvar"""
        if self.user_id and not self.autho_nickname:
            # Busca o usuário relacionado
            await self.fetch_related('user')
            self.autho_nickname = (
                f'{self.user.first_name} {self.user.last_name}'
            )

    @property
    async def author_full_name(self) -> str:
        """Retorna o nome completo do autor (propriedade async)"""
        if not self.autho_nickname:
            await self.fetch_related('user')
            return f'{self.user.first_name} {self.user.last_name}'
        return self.autho_nickname

    @property
    async def author_info(self) -> dict:
        """Retorna informações básicas do autor"""
        await self.fetch_related('user')
        return {
            'id': self.user.id,
            'full_name': f'{self.user.first_name} {self.user.last_name}',
            'photo': self.user.photo,
            'username': self.user.user_info.username
            if hasattr(self.user, 'user_info')
            else None,
        }

    async def increment_likes(self) -> None:
        """Incrementa o contador de likes"""
        self.quantity_likes += 1
        await self.save()

    async def decrement_likes(self) -> None:
        """Decrementa o contador de likes (se maior que 0)"""
        if self.quantity_likes > 0:
            self.quantity_likes -= 1
            await self.save()

    class Meta:
        table = 'posts'
        ordering = ['-created_at']  # Posts mais recentes primeiro por padrão
