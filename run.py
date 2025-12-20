from application.src.__main__ import create_app
from application.src.models.search import SearchData
import os
import sys

app = create_app()

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}")
