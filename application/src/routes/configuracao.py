import sqlite3
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from flask import render_template, Blueprint, redirect, flash, url_for, request, session
import requests
from datetime import datetime
from flask_login import current_user, login_required
from application.src.database.users.configure_users import my_db, Links, link_of_user

from application.src.models.link_validators import validate_links
from application.src.services.user_service import get_user_info, UserData
import os
from dotenv import load_dotenv

configuracao_ = Blueprint('config', __name__, template_folder='templates')
load_dotenv()


@configuracao_.route('/devorbit/configuracao/<usuario>', methods=['POST', 'GET'])
def config_account(usuario):
    # Inicializando variáveis para evitar problemas
    
    user_photo = None
    email_usuario = None
    bio = None
    status = None
    id_usuario = None
    date_create = None

    if request.method == 'POST':
        github = request.form.get('github')
        linkedin = request.form.get('linkedin')  
        site = request.form.get('site')

          
        # Validação dos links
        validateslinks = validate_links(github=github, linkedin=linkedin, site=site)
        
       
        # Validar os links
        if not validateslinks:
            flash(('github', "O link do GitHub fornecido é inválido."), "error")
        

        # Verifica se pelo menos um dos links é válido
        if validateslinks["github_valid"] or validateslinks["linkedin_valid"] or validateslinks["site_valid"]:
            user_id = session.get('user', {}).get('id')
            if not user_id:
                return redirect(url_for('login.login_page'))

            # Correção: Passar valores diretamente
            link_data = Links(
                github=github if validateslinks["github_valid"] else None,
                linkedin=linkedin if validateslinks["linkedin_valid"] else None,
                site=site if validateslinks["site_regex"] else None )
            print(link_data)
            link_of_user(link_data, user_id)
            flash("Links salvos com sucesso!", "success")
            return redirect(url_for('config.config_account', usuario=usuario))
        else:
        # Redireciona de volta com mensagens de erro
            flash("Erro ao salvar links. Verifique os links e tente novamente.", "error")
            return redirect(url_for('config.config_account', usuario=usuario))

    try:
        
        conn = sqlite3.connect(os.getenv("BANCO_DB"))
        cursor = conn.cursor()
        cursor.execute('SELECT id, photo, email, bio, date_create, banner FROM usuarios WHERE name = ?', (usuario,))

        user = cursor.fetchone()
        user_photo = user[1]
        email_usuario = user[2]
        bio = user[3]
        date_create = user[4][0:10]
        usuario = current_user.username
        id_usuario = current_user.id
        print(usuario)
        print(id_usuario)

        banner = user[5]

        searching_account_data = get_user_info(current_user.id)
        if not searching_account_data:
            return redirect(url_for('errorHttp.page_erro'))
        
        username = searching_account_data.get('username')
        user_id = searching_account_data.get('id')
       

        status = "Conta Saudável" if usuario else "Sua conta está sendo verificada."


        conn.close()

       
    except requests.exceptions.RequestException:
        flash("Erro ao carregar a página. Tente novamente mais tarde.", "error")

    finally:
        conn.close()


    return render_template('configuracao.html',  user_photo=user_photo, usuario=usuario, 
                           email_usuario=email_usuario, status=status, id_usuario=id_usuario,
                            bio=bio, date_create=date_create, banner=banner, username=username)
