from typing import List, Optional

from pydantic import BaseModel


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

