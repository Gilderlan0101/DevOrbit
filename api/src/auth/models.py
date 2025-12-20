from pydantic import Field
from tortoise import fields, models
from src.global_utils.id_generator import generate_short_id as ID_default

class User(models.Model):
    id = fields.CharField(max_length=10, pk=True, default=ID_default)

    # Informações do cliente
    username = fields.CharField(min_length=4, max_length=120)
    email = fields.CharField(max_length=150, unique=True)
    password = fields.TextField()
    status = fields.BooleanField(default=True)
    # Informações da conta
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
