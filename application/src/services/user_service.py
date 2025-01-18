from flask import flash, redirect, url_for
from application.src.database.users.configure_users import my_db
from application.src.services.api_service import dataRequests



def get_user_info(user_id):  # Busca por ID
    banco, cursor = my_db()

    # Buscar informações completas do usuário no banco
    cursor.execute(
        'SELECT id, photo, bio, github, likedin, site, followers, following, banner, name FROM usuarios WHERE id = ?',
        (user_id,)
    )
    user = cursor.fetchone()
   

    if not user:
        flash('Usuário não encontrado.', 'error')
        return None

    return [{
        'id': user[0],
        'user_photo': user[1],
        'bio': user[2],
        'github': user[3],
        'linkedin': user[4],
        'site': user[5],
        'followers': user[6],
        'following': user[7],
        'banner': user[8],
        'username': user[9]
    }]



    

def UserData(usuario): # This function receives current_user.id:
    banco, cursor = my_db()
    






    # Fetch the logged-in user's information:
    cursor.execute(
        'SELECT id, name,  occupation FROM user_information WHERE id = ?',
        (usuario,)
    )
    user = cursor.fetchone()
   
    if not user:
        flash('Usuário não encontrado.', 'error')
        return redirect(url_for('home.home_page'))  # Redireciona caso o usuário não seja encontrado

     # Directly return a dictionary list with the information
    return [{
        'id': user[0],
        'username': user[1],
        'occupation': user[2]
        
    }]


def get_infor_comment(user_id):  
    """Busca as informações do usuário pelo seu ID."""
    banco, cursor = my_db()  # Conecta ao banco de dados

    # Consulta as informações do usuário
    cursor.execute(
        'SELECT id, name, photo FROM usuarios WHERE id = ?',
        (user_id,)
    )
    user = cursor.fetchone()
    
    print("Dados do usuário:", user)

    if not user:
        print(f"Usuário com ID {user_id} não encontrado.")
        return None

    print(f"Usuário encontrado: {user}")  # Log para ver os dados
    return {
        'id': user[0],
        'username': user[1],
        'photo': user[2] or 'icon/default.svg'  # Foto padrão
    }


def enrich_posts_with_user_info(posts):
    """
    Enriquecimento dos posts com id e nome dos usuários nos comentários.
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
                    comment['username'] = "Desconhecido"

            enriched_comments.append(comment)

        # Atualiza os comentários no post
        post['comments'] = enriched_comments
        enriched_posts.append(post)

    return enriched_posts
