from application.src.__main__ import cache
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    url_for,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from application.src.database.configure_post import criando_post
from dotenv import load_dotenv
import requests
import os
import logging

load_dotenv()


@login_required
def make_cache_key():
    """
    Gera uma chave única de cache para cada usuário logado.
    Combina o ID do usuário e o caminho da requisição.
    """
    return f'{current_user.id}:{request.path}'


posts = Blueprint('page_posts', __name__, template_folder='templates')


@cache.cached(timeout=60)
@posts.route('/devorbit/feed/posts/', methods=['POST', 'GET'])
@login_required
def create_post_route():
    if request.method == 'POST':
        try:

            # Coletar dados do formulário
            titulo = request.form.get('titulo')  # name="titulo"
            post_content = request.form.get('post')  # name="post"
            post_image = request.files.get('file')  # name="file"
            username = current_user.username  # Nome do usuário logado

        except Exception as e:
            flash(f'Erro ao criar o post: {str(e)}', 'error')
            logging.info('Error: ', e.__class__.__name__)
            with open(os.getenv('LOGS'), 'w') as f:
                f.write('{}\n'.format(e.__class__.__name__))
            return redirect(request.url)

    return render_template(
        'post.html', username=current_user.username, id=current_user.id
    )
