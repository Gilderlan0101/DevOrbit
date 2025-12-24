from fastapi import APIRouter, Depends, HTTPException, Security, status

from src.auth.dependencies import get_current_active_user, get_current_user
from src.auth.schemas import SystemUser
from src.global_utils.i_request import permitted_origin
from src.post.schemas import CreatePost, PostUpdateBase
from src.post.service import PostService

router = APIRouter(tags=['CRUD_POST'], prefix='/devorbit')

# Public
@router.get('/feed/posts/', summary='Buscar todos os posts')
async def get_all_posts(
    origin: bool = Depends(permitted_origin),
):
    try:
        post_service = PostService()
        posts = await post_service.get_posts_formatted()
        return posts

    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Serviço temporariamente indisponível. Banco de dados offline.',
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro ao processar posts: {str(e)}',
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Erro interno no servidor. {str(e)}',
        )


@router.post('/create/posts/', summary='Criar novo post')
async def send_posts_in_community(
    data: CreatePost,
    origin: bool = Depends(permitted_origin),
    current_user: SystemUser = Security(
        get_current_user, scopes=['user:write']
    ),
):

    init_service = PostService()

    var = await init_service.post_create(
        data=dict(data), user_id=current_user.id, username=current_user.email
    )

    return var


@router.delete('/delete_posts/{post_id}', summary='Deletar post')
async def deleted_posts(
    post_id: int,
    origin: bool = Depends(permitted_origin),
    current_user: SystemUser = Security(
        get_current_user, scopes=['user:write']
    ),
):

    init_service = PostService()
    var = await init_service.delete_post(
        user_id=current_user.id, post_id=post_id
    )
    return var


@router.put('/upgrade_posts/{post_id}', summary='Atualizar post')
async def upgrade_posts_for_user(
    post_id: int,
    content: PostUpdateBase,
    origin: bool = Depends(permitted_origin),
    current_user: SystemUser = Security(
        get_current_user, scopes=['user:write']
    ),
):

    from src.auth.models import User as db
    from src.global_utils.i_request import get_user

    get_current_user = await get_user(db=db, username=current_user.email)
    if not get_current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado.',
        )

    init_service = PostService()
    var = await init_service.post_update_info(
        user_id=current_user.id, post_id=post_id, content=dict(content)
    )
    return var
