from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user

from application.src.database.users.configure_users import add_user_information
from application.src.models.modelsUser import UserInformation

username_unic = Blueprint(
    'username_page', __name__, template_folder='templates'
)
termosEcondicao = Blueprint('temos', __name__, template_folder='templates')


@username_unic.route('/devorbit/username/', methods=['GET', 'POST'])
def register_username():
    # Verifica se o usuário está na sessão
    if 'user' not in session:
        flash('Por favor, complete a primeira etapa do cadastro.', 'error')
        return redirect(url_for('register.page_register'))

    if request.method == 'POST':
        # Obtém os dados do formulário
        username = request.form['username']
        profession = request.form['profession']
        # Falta 2 campos

        # Recupera os dados da sessão
        user_name = current_user.username
        user_email = session['user']['email']

        # Cria o objeto UserInformation
        account_information = UserInformation(
            username=username,
            name=user_name,  # Usa o nome armazenado na sessão
            email=user_email,
            occupation=profession,
        )

        if account_information:
            # Salva as informações no banco de dados
            add_user_information(account_information)

        current_user.username = username
        current_user.email = user_email

        # Autentica o usuário novamente após o cadastro
        login_user(current_user)

        flash('Usuário cadastrado com sucesso!', 'success')

        # Redireciona para a página inicial
        return redirect(url_for('home.home_page'))

    # Renderiza o formulário
    return render_template('create_username.html', methods=['POST'])


@termosEcondicao.route('/devorbit/termos/', methods=['GET', 'POST'])
def termos():
    if request.method == 'POST':
        flash('Termos aceitos com sucesso!', 'success')
        return redirect(url_for('username_page.register_username'))
    return render_template('termos.html')
