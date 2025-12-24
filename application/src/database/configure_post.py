import sqlite3
from pydantic import BaseModel


class Post(BaseModel):
    """
    Modelo para dados do post.
    Campos obrigatórios:
    - nome: Nome do usuário.
    - img_path: Caminho da imagem associada ao post (opcional).
    """

    nome: str  # Nome do autor
    img_path: str = None  # Caminho da imagem (opcional)


def banco_post():
    """
    Conexão com o banco de dados.
    Retorna uma tupla contendo a conexão e o cursor.
    """
    banco = sqlite3.connect('banco_posts_comunidade.db', timeout=5)
    return banco, banco.cursor()


def criar_tabela_post():
    """
    Cria a tabela `post_do_usuario` no banco de dados, se ela não existir.
    """
    banco, cursor = banco_post()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS post_do_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            img_path TEXT NULL,  -- Permite que o campo img_path seja NULL
            data TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    banco.commit()
    banco.close()


def criando_post(novo_post: Post):
    """
    Insere um novo post no banco de dados.
    Retorna o ID do post criado.
    """
    with sqlite3.connect('banco_posts_comunidade.db', timeout=10) as banco:
        cursor = banco.cursor()

        cursor.execute(
            """
            INSERT INTO post_do_usuario (nome, img_path)
            VALUES (?, ?)
            """,
            (novo_post.nome, novo_post.img_path),
        )
        banco.commit()
        return cursor.lastrowid  # Retorna o ID do novo post criado
