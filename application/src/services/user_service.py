from flask import flash, redirect, url_for
from application.src.database.users.configure_users import my_db
from application.src.services.api_service import dataRequests
import logging


def get_user_info(user_id):  # Busca por ID | usuario logado | Dono da conta
    banco, cursor = my_db()

    # Buscar informações completas do usuário no banco
    cursor.execute(
        'SELECT id, photo, bio, github, likedin, site, followers, following, banner, name FROM usuarios WHERE id = ?',
        (user_id,),
    )
    user = cursor.fetchone()
    print(user)

    if not user:
        logging.warning(f'User with ID {user_id} not found.')
        return None  # Ou uma lista vazia, dependendo do contexto

    return {
        'id': user[0],
        'user_photo': user[1],
        'bio': user[2],
        'github': user[3],
        'linkedin': user[4],
        'site': user[5],
        'followers': user[6],
        'following': user[7],
        'banner': user[8],
        'username': user[9],
    }


def UserData(usuario):   # This function receives current_user.id:
    (
        banco,
        cursor,
    ) = (
        my_db()
    )  # Devemos usar essa função para mostra recomendaçoes no celular

    # Fetch the logged-in user's information:
    cursor.execute(
        'SELECT id, name,  occupation FROM user_information WHERE id = ?',
        (usuario,),
    )
    user = cursor.fetchone()

    if not user:
        # caso o usuario / user_id não for encontrado
        logging.info('user not found')
        return None

    # Directly return a dictionary list with the information
    return {
        'id': user[0],
        'username': user[1],
        'occupation': user[2].capitalize(),
    }


def get_infor_comment(user_id):
    banco, cursor = my_db()

    # Consulta as informações do usuário
    cursor.execute(
        'SELECT id, name, photo FROM usuarios WHERE id = ?', (user_id,)
    )
    user = cursor.fetchone()

    if not user:
        logging.info('user not found')
        return None

    return {
        'id': user[0],
        'username': user[1],
        'photo': user[2] or 'icon/default.svg',  # Foto padrão
    }


def enrich_posts_with_user_info(posts):
    """
    Enriquecimento dos posts com id e nome dos usuários nos comentários.
    Essa função buscar pegar o id do usuario que comentou em um post, com o id do usuario buscamos informaçoes sobre
    ele. como (foto e nome).
    """
    enriched_posts = []

    for post in posts:
        # Garantir que a chave 'comments' é uma lista
        if 'comments' not in post or not isinstance(post['comments'], list):
            continue

        enriched_comments = []
        for comment in post['comments']:
            # Certifique-se de que 'user_id' existe no comentário
            if 'user_id' in comment:
                user_id = comment['user_id']
                user_info = get_infor_comment(user_id)
                if user_info:
                    # Enriquecer o comentário apenas com 'id' e 'username'
                    comment['user_id'] = user_info['id']
                    comment['username'] = user_info['username']
                    comment['photo'] = user_info['photo']
                else:
                    # Adicionar informações padrão se o usuário não for encontrado
                    comment['photo'] = None
                    comment['username'] = 'Desconhecido'

            enriched_comments.append(comment)

        # Atualiza os comentários no post
        post['comments'] = enriched_comments
        enriched_posts.append(post)

    return enriched_posts
