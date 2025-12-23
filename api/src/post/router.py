from fastapi import APIRouter, Depends, HTTPException, status
from src.post.schemas import CreatePost
from src.post.service import PostService
from src.global_utils.i_request import permitted_origin

router = APIRouter(tags=['CRUD_POST'], prefix='/devorbit')

@router.get('/feed/posts/', summary="Buscar todos os posts")
async def get_all_posts(origin=Depends(permitted_origin)):
    try:
        post_service = PostService()
        posts = await post_service.get_posts_formatted()
        return posts

    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço temporariamente indisponível. Banco de dados offline."
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar posts: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no servidor. {str(e)}"
        )

@router.post('/create/posts/', summary="Criar novo post")
async def send_posts_in_community(data: CreatePost, origin=Depends(permitted_origin)):
    init_service = PostService()
    var = await init_service.post_create(data=dict(data))
    return var

@router.delete('/delete_posts', summary="Deletar post")
async def deleted_posts(origin=Depends(permitted_origin)):
    init_service = PostService()
    var = await init_service.delete_post(user_id="476347", post_id="768498")
    return var

@router.put('/upgrade_posts', summary="Atualizar post")
async def upgrade_posts_for_user(origin=Depends(permitted_origin)):
    pass
