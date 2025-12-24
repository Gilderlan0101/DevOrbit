from dotenv import load_dotenv
import os
import sqlite3
import random
import logging

# Carregar variáveis de ambiente
load_dotenv()


# Esta def so deve ser exibida no celular


# Função para formatar nomes de usuários
def format_user_name(full_name):
    # Divide o nome completo em palavras
    name_parts = full_name.split()

    # Pega o primeiro nome, ou um valor padrão se o nome estiver vazio
    if name_parts:
        first_name = name_parts[0]
    else:
        return 'Usuário'

    # Limita o comprimento do nome (por exemplo, no máximo 10 caracteres)
    max_length = 10
    if len(first_name) > max_length:
        return first_name[:max_length] + '...'  # Trunca nomes longos
    return first_name


# Pegar todos os usuários e mostrar 0-10 no front como recomendação
def recommendationsUser():
    db_path = os.getenv(
        'BANCO_DB', 'usuarios.db'
    )  # Obtém o caminho do banco de dados
    try:
        # Conecta ao banco de dados
        banco = sqlite3.connect(db_path)
        cursor = banco.cursor()

        # Define um limite aleatório
        limit = random.randint(2, 4)

        # Busca os dados das tabelas
        query = f"""
        SELECT usuarios.id, usuarios.name, usuarios.photo, user_information.occupation
        FROM usuarios
        INNER JOIN user_information ON usuarios.id = user_information.id
        LIMIT {limit}
        """
        cursor.execute(query)
        get_information_user = cursor.fetchall()

        # Formata os dados para exibição
        recommendations = []
        for user in get_information_user:
            recommendations.append(
                {
                    'id': user[0],  # ID do usuário
                    'name': user[1],  # Nome do usuário
                    'user_photo': user[2],  # Foto do usuário
                    'occupation': user[3],  # Ocupação do usuário
                }
            )

        random.shuffle(recommendations)
        # Retorna os dados formatados
        return recommendations

    except Exception as e:
        logging('Error when searching for users ', e.__class__.__class__)
        return []
    finally:
        banco.close()  # Sempre feche a conexão ao terminar
