from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user

from application.src.__main__ import cache
from application.src.database.users.configure_users import (
    User,
    check_user_login,
)
from application.src.models.modelsUser import Login

login_ = Blueprint("login", __name__, template_folder="templates")


@cache.cached(timeout=5)
@login_.route("/devorbit/login/", methods=["POST", "GET"])
def login_page():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # remember_me = request.form['remember_me']
        # futuramente salva o usuario na session para não precisa
        # realiza login novamente

        # Verificar o login
        try_login = Login(email, password)
        is_valid, user_id, pwd, username = check_user_login(try_login)

        if try_login and is_valid:
            # Cria a instância do usuário com o ID e o nome
            user = User(user_id, username, email)
            # Faz login do usuário usando Flask-Login
            login_user(user)

            # Adiciona informações do usuário na sessão
            session["user"] = {
                "name": current_user.username,
                "id": current_user.id,
            }

            # Redireciona para a página desejada ou para a home
            next_page = session.get("next", url_for("home.home_page"))
            return redirect(next_page)
        else:
            return redirect(url_for("login.login_page"))

    return render_template("login.html")