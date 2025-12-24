"""UTF-8"""
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
from flask_login import current_user
from application.src.database.users.configure_users import my_db
from application.src.utils.terminal import clear_terminal
from application.src.__main__ import cache


import logging

import httpx
import sqlite3
import os

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
load_dotenv()


def make_cache_key():
    """
    Gera uma chave única de cache para cada usuário logado.
    Combina o ID do usuário e o caminho da requisição.
    """
    return f'{current_user.id}'


@cache.cached(timeout=5000, key_prefix=make_cache_key)
def get_user_info(user_id):
    """
    Esta função serve para busca dados padrão caso algum tipo de dado do usuario não esteja em
    (user_information) Podemos resgata os dados aqui
    """
    banco, cursor = my_db()

    # Buscar informações completas do usuário no banco
    cursor.execute(
        'SELECT id, photo, bio, github, likedin, site, followers, following, banner, name FROM usuarios WHERE name = ?',
        (user_id,),
    )
    user = cursor.fetchone()

    if not user:

        return None

    return [
        {
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
    ]


def fetch_api_data() -> list:
    """Faz requisição à API e retorna os dados formatados como lista."""
    try:
        response = httpx.get(os.getenv('API'), timeout=10)
        print(response)
        print(
            f'Resposta da API: {response.status_code}'
        )  # Para debugging, remova antes de produção

        if response.status_code != 200 or not response.is_success:   # bool
            print(f'Erro na API: {response.status_code}')
            return []

        try:
            posts = response.json()
            if not isinstance(posts, list):

                return list(posts)
            return posts
        except ValueError:
            print('Erro ao converter a resposta para JSON')
            return []
    except httpx.HTTPStatusError as e:
        # log_error(e)
        return []
    except Exception as e:
        print(e.__class__.__name__)


def fetch_database_data() -> Dict:
    """Busca informações complementares do banco de dados SQLite."""
    try:
        conn = sqlite3.connect(os.getenv('BANCO_DB'))
        cursor = conn.cursor()

        # Buscar fotos dos usuários
        cursor.execute('SELECT name, photo FROM usuarios')
        user_photos = dict(cursor.fetchall())

        # Buscar nomes de usuário e ocupações
        cursor.execute(
            'SELECT name, username, occupation FROM user_information'
        )
        user_usernames = {
            name: {'username': username, 'occupation': occupation}
            for name, username, occupation in cursor.fetchall()
        }
        logging.debug('fetching user data')

        return {'user_photos': user_photos, 'user_usernames': user_usernames}
    except sqlite3.Error as e:
        logging.critical(
            f'Erro no banco de dados: {e.__class__.__name__}: line 63'
        )
        return {'user_photos': {}, 'user_usernames': {}}
    finally:
        conn.close()


def format_posts(posts: list, db_data: Dict) -> Dict:
    try:
        """Formata os dados dos posts com informações do banco de dados."""

        user_photos = db_data.get('user_photos', {})
        user_usernames = db_data.get('user_usernames', {})
        best_post_list = []

        for post in posts:

            real_name = post.get('nome', 'Desconhecido')

            # Esta variavel pegar o nome do usuario caso não seja encontrado o
            # username || nome de usuario em (user_info)
            Users_default_name = post.get('nome', 'Desconhecido')
            variavel = get_user_info(
                Users_default_name
            )  # Nome padrão do usuario

            user_info = user_usernames.get(
                real_name,
                {
                    'username': variavel[0]['username'],
                    'occupation': 'Desconhecido',
                },
            )
            comments = post.get(
                'comments', [{'comment': 'Ainda não há comentários'}]
            )

            if 'username' not in user_info:
                logging.warning(
                    f"Usuário {real_name} não tem 'username'. Dados: {user_info}"
                )

            formatted_comments = [
                {
                    'comentario_id': comment.get('comment_id', 0),
                    'comment': comment.get('comment'),
                    'date_creation': comment.get('creation_date', ''),
                    'user_id': comment.get('user_id', None),
                }
                for comment in comments
            ]

            best_post_list.append(
                {
                    'id': int(post['id']),
                    'nome': user_info['username'],
                    'titulo': post.get('titulo', 'Sem título'),
                    'data': post.get('data', '00:00')[11:16],
                    'post': post.get('post', '').capitalize(),
                    'likes': int(post.get('likes', 0)),
                    'img_url': post.get('img_url', None),
                    'user_photo': user_photos.get(real_name, None),
                    'user_id': int(post['user_id']),
                    'occupation': user_info['occupation'],
                    'comments': formatted_comments
                    if formatted_comments
                    else [{'Ainda não há comentários'}],
                }
            )

    except KeyError as erro:
        clear_terminal()
        logging.critical(
            f'Erro: {erro.__class__.__name__}: keyerro (best_post_list)'
        )
        return [
            {
                'id': 0,
                'nome': 'Desconhecido',
                'titulo': 'Erro ao carregar post',
                'data': '00:00',
                'post': 'Não foi possível carregar o conteúdo.',
                'likes': 0,
                'img_url': None,
                'user_photo': None,
                'user_id': 0,
                'occupation': 'Desconhecido',
                'comments': [
                    {
                        'comentario_id': 0,
                        'comment': 'Erro ao carregar comentários',
                        'date_creation': '',
                        'user_id': None,
                    }
                ],
            }
        ]

    except TypeError as erro:
        clear_terminal()
        logging.error(
            f'Errp: {erro.__class__.__name__} Erro de tipo em (best_post_list)'
        )
        return best_post_list.append(
            {
                'id': post['id'],
                'nome': user_info['username'],
                'titulo': 'Erro ao carregar conteúdo.',
                'data': post.get('data', '00:00')[11:16],
                'post': 'Erro ao carregar conteúdo.',
                'likes': int(post.get('likes', 0)),
                'img_url': None,
                'user_photo': user_photos.get(real_name, None),
                'user_id': post['user_id'],
                'occupation': user_info['occupation'],
                'comments': formatted_comments
                if formatted_comments
                else [{'Ainda não há comentários'}],
            }
        )
    except AttributeError as erro:
        logging.critical(erro)

    featured_posts = [post for post in best_post_list if post['likes'] >= 1]
    banner = {
        'post_titulo': os.getenv('MENSAGEN', 'Fala Dev!'),
        'post': os.getenv(
            'MENSAGEN_POST',
            'Os melhores posts vão aparecer aqui! 🌟 Não deixe de comentar e compartilhar suas ideias. Vamos juntos criar uma comunidade incrível!',
        ),
        'nome': os.getenv('CODECHAMBER', 'DEV ORBIT'),
    }

    if featured_posts:
        banner = featured_posts[0]

    return {'todos_os_posts': best_post_list, 'post_banner': banner}


def dataRequests() -> Dict:
    """Processa dados da API e do banco de dados, retornando um dicionário formatado."""
    try:
        posts = fetch_api_data()
        db_data = fetch_database_data()
        logging.info(f'all data has been loaded')
        return format_posts(posts, db_data)

    except Exception as e:
        logging.error(
            f'Error processing API data: {e.__class__.__name__}: line 125'
        )
        logging.critical(f'processing error: {e.__class__.__name__}: line 126')
        # log_error(e)
        return fetch_api_data()

    except httpx.exceptions.ConnectionError as e:
        clear_terminal()
        logging.error(
            f'failed to connect to the server: {e.__class__.__name__}: line 231'
        )
        # log_error(e)
        return {}
