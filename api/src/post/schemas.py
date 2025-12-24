from typing import List, Optional

from pydantic import (BaseModel, EmailStr, Field, field_validator, validator,
                      validators)


class CreatePost(BaseModel):
    """
    Schemas responsavel por cria um post  na cumunidade.
    """

    title: str
    content: str
    photo: Optional[str] | None


class ResponseRenderPost(BaseModel):
    user_id: int
    post_id: int
    username: str
    title: str
    content: str
    photo: Optional[str] | None
    quantity_like: int
    comments: Optional[List[str]] | None
    date: str

    model_config = {'from_attributes': True}


class PostUpdateBase(BaseModel):

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description='Título do post'
    )
    content: Optional[str] = Field(
        None, min_length=1, description='Conteúdo do post'
    )
    photo: Optional[str] = Field(None, description='URL da imagem do post')
    is_published: Optional[bool] = Field(
        None, description='Se o post está publicado'
    )
    tags: Optional[str] = Field(
        None, description='Tags do post separadas por vírgula'
    )
    # comment_disabled: Optional[bool] = Field(None, description="Se comentários estão desabilitados")
    # visibility: Optional[bool] = Field(None, description="Visibilidade do post")
    # category_id: Optional[int] = Field(None, gt=0, description="ID da categoria")
    # status: Optional[str] = Field(None, description="Status do post (rascunho, revisão, publicado)")

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is not None and v.strip() == 'string':
            return None
        return v

    @field_validator('title', 'content', 'photo')
    def validate_not_empty_string(cls, v, field):
        if v is not None and v.strip() in ['string', '']:
            return None
        return v

    class Config:
        extra = 'ignore'  # Ignora campos extras não definidos
