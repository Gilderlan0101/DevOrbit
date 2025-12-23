from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from tortoise.exceptions import DBConnectionError, OperationalError
from datetime import datetime
from src.global_utils.i_request import get_user
from src.post.models import Posts
from src.auth.models import User as db
from src.post.schemas import ResponseRenderPost


class PostService:
    def __init__(self) -> None:
        self.flag = False

    async def get_all_posts(self) -> List[Dict[str, Any]]:
        try:
            all_posts = await Posts.filter(
                is_deleted=False,
                is_published=True
            ).prefetch_related('user').order_by('-created_at')

            if not all_posts:
                return []

            posts_list = []
            for post in all_posts:
                if not post.user:
                    await post.fetch_related('user')

                author_username = None
                if hasattr(post.user, 'first_name') and post.user.full_name:
                    author_username = post.user.full_name

                post_dict = {
                    "id": post.id,
                    "user_id": post.user_id, # type: ignore
                    "title": post.title,
                    "content": post.content,
                    "autho_nickname": post.autho_nickname,
                    "quantity_likes": post.quantity_likes,
                    "photo": post.photo if post.photo != "string" else None,
                    "category": post.category,
                    "tags": post.tags if post.tags else [],
                    "is_published": post.is_published,
                    "is_deleted": post.is_deleted,
                    "created_at": post.created_at.isoformat() if post.created_at else None,
                    "updated_at": post.updated_at.isoformat() if post.updated_at else None,
                    "author_username": author_username,
                    "author_photo": post.user.photo if post.user else None
                }
                posts_list.append(post_dict)

            return posts_list

        except DBConnectionError:
            raise ConnectionError("Erro de conexão com o banco de dados. Tente novamente.")
        except OperationalError:
            raise RuntimeError("Erro ao processar a consulta no banco de dados.")
        except Exception as e:
            raise RuntimeError(f"Erro interno ao buscar posts. {str(e)}")

    async def get_posts_formatted(self) -> List[ResponseRenderPost]:
        try:
            posts_data = await self.get_all_posts()
            formatted_posts = []

            for post in posts_data:
                formatted_post = ResponseRenderPost(
                    user_id=post.get('user_id', ''),
                    post_id=post.get('id', ''),
                    username=post.get('author_username'), # type: ignore
                    title=post.get('title', ''),
                    content=post.get('content', ''),
                    photo=post.get('photo'),
                    quantity_like=post.get('quantity_likes', 0),
                    comments=[],
                    date=post.get('created_at', datetime.now().isoformat())
                )
                formatted_posts.append(formatted_post)

            return formatted_posts
        except Exception:
            raise

    async def post_create(self, data: dict, user_id: int, username: str):
        try:
            security_verification = await get_user(db=db,  username=username)

            if not security_verification:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Usuário não encontrado',
                )

            account_target = await Posts.create(
                autho_nickname=security_verification.full_name,
                title=data['title'],
                content=data['content'],
                photo=data['photo'],
                user_id=user_id,
            )

            if account_target:
                return {
                    'status_code': status.HTTP_201_CREATED,
                    'detail': 'Post criado com sucesso.',
                    'post': {
                        'id': account_target.id,
                        'title': account_target.title,
                    },
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Falha ao criar o post.',
                )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Erro ao criar post {str(e)}',
            )

    async def delete_post(self, user_id: str, post_id: str):
        try:
            target_post = await Posts.filter(user_id=user_id, id=post_id).first()

            if target_post:
                await target_post.delete()
                return {
                    'status_code': status.HTTP_200_OK,
                    'detail': 'Post excluído com sucesso.',
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Erro ao tentar excluir um post. Tente novamente',
                )

        except ValueError:
            raise ValueError(f"""
                A função [delete_post] só aceita valores do tipo string.
                Valores fornecidos: user_id: {type(user_id)} post_id: {type(post_id)}
            """)
        except DBConnectionError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Erro de conexão com o banco: {str(e)}'
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Erro interno: {str(e)}'
            )
