import sqlite3


def my_db():
    banco = sqlite3.connect('usuarios.db')
    return banco, banco.cursor()
