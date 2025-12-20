import sqlite3
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash
from application.src.models.modelsUser import (Cadastro, Login, Links, UserInformation)



    
def my_db():
    banco = sqlite3.connect('usuarios.db')
    return banco, banco.cursor()

def create_database():
    banco, cursor = my_db()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_create TEXT DEFAULT (datetime('now', 'localtime')),
        name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER,
        password TEXT NOT NULL,
        photo TEXT DEFAULT 'application/src/static/uploads/1.jpg',
        github TEXT NULL,
        likedin TEXT NULL,
        site TEXT NULL
        )'''
    )
   

     # Criação da tabela `user_information` com relação ao `usuarios`
     # Essas duas TABELAS devem continua tendo relação com o id , para buscar as infor do usuario etc..
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS user_information(
        id INTEGER PRIMARY KEY,  -- Mesmo ID da tabela `usuarios`
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        occupation TEXT NULL,
        FOREIGN KEY (id) REFERENCES usuarios (id) ON DELETE CASCADE
        )'''
    )
    banco.commit()
    banco.close()
    
def add_user(cadastro: Cadastro):
    banco, cursor = my_db()
    
    try:
        # Gerar o hash da senha
        senha_hash = generate_password_hash(cadastro.password).decode('utf-8')
        
        # Inserir na tabela `usuarios`
        cursor.execute('''
        INSERT INTO usuarios (name, last_name, email, age, password)
        VALUES (?, ?, ?, ?, ?)
        ''', (cadastro.name, cadastro.last_name, cadastro.email, cadastro.age, senha_hash))
        
        # Confirmar as transações
        banco.commit()
    
    except Exception as e:
        banco.rollback()
        print(f"Erro ao adicionar usuário: {e}")
    
    finally:
        banco.close()


def add_user_information(user: UserInformation):
    banco, cursor = my_db()
    
    try:
        # Inserir na tabela `user_information`
        cursor.execute('''
        INSERT INTO user_information (name, username, email, occupation)
        VALUES (?, ?, ?, ?)
        ''', (user.name, user.username, user.email, user.occupation))
        
        # Confirmar as transações
        banco.commit()
        print("Usuário adicionado com sucesso!")
        print("Usuário adicionado com sucesso!")
    
    except Exception as e:
        banco.rollback()
        print(f"Erro ao adicionar informações do usuário: {e}")
    
    finally:
        banco.close()


def check_user_login(login: Login):
    banco, cursor = my_db()
    cursor.execute('''
    SELECT id, name, password FROM usuarios WHERE email = ?
    ''', (login.email,))
    user = cursor.fetchone()
    banco.close()

    if user:
        user_id, username, hashed_password = user
        # Verifique a senha usando check_password_hash
        if check_password_hash(hashed_password, login.password):
            return True, user_id, hashed_password, username
    return False, None, None, None


# Função para adicionar a coluna 'bio' se não existir
# add column e usada para cria novas coluunas teste, para não precisar excluir o banco
def add_column():
    banco, cursor = my_db()
    
    # Verifica se a coluna 'bio' já existe
    cursor.execute("PRAGMA table_info(usuarios)")
    columns = [column[1] for column in cursor.fetchall()]  # Obtém todos os nomes das colunas

    if 'bio' not in columns:
        # Adiciona a coluna 'bio' à tabela 'usuarios'
        cursor.execute("ALTER TABLE usuarios ADD COLUMN bio TEXT")
        banco.commit()
       
    else:
        pass
    if 'followers' not in columns:
        # add followers
        cursor.execute("ALTER TABLE usuarios ADD COLUMN followers INTEGER DEFAULT 0")
        banco.commit()

    else:
        pass

    if 'following' not in columns:
        # add following
        cursor.execute("ALTER TABLE usuarios ADD COLUMN following INTEGER DEFAULT 0")
        banco.commit()
        
    else:
        pass

    if 'banner' not in columns:
        # banner de perfil do usuario
        cursor.execute("ALTER TABLE usuarios ADD COLUMN banner TEXT")
        banco.commit()
    
    else:
        pass

    if 'is_first_login' not in columns:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN is_first_login BOOLEAN DEFAULT 1")
        banco.commit()
    else:
        pass

   

    banco.close()

def link_of_user(link: Links, user_id: int):
    banco, cursor = my_db()
    try:
        # Atualiza os campos github, linkedin e site do usuário com o ID especificado
        cursor.execute('''
        UPDATE usuarios
        SET github = ?, likedin = ?, site = ?
        WHERE id = ?
        ''', (link.github, link.linkedin, link.site, user_id))
        banco.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro ao salvar dados: {e}")
    except sqlite3.OperationalError as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    finally:
        banco.close()




class User(UserMixin):
    def __init__(self, user_id: str, username: str, email: str):
        self.id = user_id
        self.username = username
        self.email = email

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        banco, cursor = my_db()
        cursor.execute('SELECT id, name, email FROM usuarios WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        banco.close()
        if user:
            print(f'ID: {user[0]}, Username: {user[1]}, Email: {user[2]}')  # Verificando se os dados estão corretos
            return User(user_id=user[0], username=user[1], email=user[2])
        return None
