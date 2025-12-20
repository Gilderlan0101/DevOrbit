import logging
import traceback
import httpx

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from application.src.__main__ import cache
from application.src.models.recommendations import recommendationsUser
from application.src.utils.terminal import clear_terminal

from application.src.services.api_noticias import (
    get_exact_count,
    get_top_stories,
)
from application.src.services.api_service import dataRequests
from application.src.services.user_service import (
    enrich_posts_with_user_info,
    get_user_info,
)


# Configuração do Blueprint
home_ = Blueprint("home", __name__, template_folder="templates")


@login_required
def make_cache_key():
    """
    Gera uma chave única de cache para cada usuário logado.
    Combina o ID do usuário e o caminho da requisição.
    """
    return f"{current_user.id}:{request.path}"


@home_.route("/devorbit/feed/", methods=["POST", "GET"])
@cache.cached(timeout=100, key_prefix=make_cache_key)
def home_page():
    try:
        data = dataRequests()  # Request post data
        data_noticias = get_top_stories(num_noticias=get_exact_count())
        # data_comment_user = get_infor_comment()

        if (
            not isinstance(data, dict)
            or "todos_os_posts" not in data
            or "post_banner" not in data
        ):
            return redirect(url_for("errorHttp.page_erro"))

        posts = data["todos_os_posts"]  # Get the posts
        post_banner = data["post_banner"]

        # Buscando informações do usuário logado
        user_data = get_user_info(current_user.id)
        if not user_data:
            clear_terminal()
            logging.info("usuario não encotrado.")
            return redirect(url_for("home.home_page"))

        username = user_data.get("username")
        user_id = user_data.get("id")
        photo_user_profile = user_data.get("user_photo", None)

        # 1. Chama a função `dataRequests()` para obter os dados da API ou
        #  banco de dados,
        # que geralmente retorna um dicionário contendo várias informações,
        #  incluindo os posts.
        var = dataRequests()
        # 2. Extrai apenas os posts da resposta retornada, acessando a chave
        #  "todos_os_posts".
        # Isso garante que a variável `posts` contenha apenas a lista de posts
        #  para ser processada.
        posts = var["todos_os_posts"]  # Extrai apenas os posts
        # 3. Envia a lista de posts para a função
        # `enrich_posts_with_user_info()`,
        # que adiciona informações adicionais aos comentários, como nome e foto
        #  do autor.
        # O resultado enriquecido é armazenado em `enriched_posts`.
        enriched_posts = enrich_posts_with_user_info(posts)


       


        recommendations = recommendationsUser()  # Prepare recomendações
        likes = [
            post["likes"] for post in posts if post["likes"] >= 0
        ]  # Filtros ou lógica adicional para os posts

        if current_user.is_authenticated:
            return render_template(
                "home.html",
                username=username,
                usuario=current_user.username,
                photo_user_profile=photo_user_profile,
                id=current_user.id,
                posts=posts,
                post_banner=post_banner,
                recommendations=recommendations,
                likes=likes,
                data_noticias=data_noticias,
                foto_commet=enriched_posts,
            )
        else:
            return render_template(
                "home.html",
                id=user_id,
                posts=posts,
                post_banner=post_banner,
                likes=likes,
            )

    except Exception as e:  # capturing error and saving to a log file
        # Capture traceback for deeper debugging
        clear_terminal()
        error_message = (
            f"Error loading homepage: {e.__class__.__name__} - {str(e)}"
        )
        stack_trace = traceback.format_exc()
        

        # Log critical error with traceback
        logging.critical(f"{error_message}\n{stack_trace}")

        # Optionally log more details, such as the request URL or user info
        logging.critical(f"Request URL: {request.url}")
        logging.critical(
            "User ID: "
            + str(
                current_user.id
                if current_user.is_authenticated
                else "Not authenticated"
            )
        )

        # Return to error page or render a custom message
        return redirect(url_for("errorHttp.page_erro"))

    except httpx.exceptions.InvalidURL as erro:
        clear_terminal()
        logging.info(erro)
        logging.info(erro.__name__.__class__)
        return redirect(url_for("home_home_page"))