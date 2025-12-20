# main
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.database.init_database import init_database, close_database
from src.global_utils.i_request import permitted_origin

load_dotenv(dotenv_path=Path(__file__).parent / '.env.local')


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    await init_database()
    print("Banco de dados inicializado")

    yield

    await close_database()
    print("Banco de dados desconectado")




class Main:
    def __init__(self) -> None:

        # Carregar todos os metadados em self.app(**metadados)
        self.app = FastAPI(lifespan=lifespan)

        # Inicia dados e rotas iniciais
        self.setup_middlewares()
        self.start_routes()

    def setup_middlewares(self):
        """Configuração de CORS da aplicação
        Atualmente servindo NEXT.js
        """

        origins = ['http://127.0.0.1:3000']   # Atualmente apenas um destino
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )

    def start_routes(self):
        """Local onde adicionamos nossas rotas.
        Para manter a elegancia do codigo vamos carregar
        todas as rotas a partir de uma função externa.
        """

        # Rota default para testar a api.
        @self.app.get('/health')
        async def root(request: Request, origin=Depends(permitted_origin)):
            """Apenas o servidor back end e o front end pode
            fazer requests para essa rota.
            """

            # Se for uma request de um servidor permitido
            # a resposta sera esta abaixo
            return {
                'status': 'healthy',
                'service': 'FastAPI',
                'allowed_origin': request.headers.get('host', 'Host'),
            }

        from src.auth.router import router as register
        self.app.include_router(register)

    def run(self, host: str = '0.0.0.0', port: int = 8000):
        """Inicia o servidor
        Esse metodo deve descobrir se esta em produção ou em desenvolvimento.
        """

        environment = os.getenv('ENVIRONMENT', None)

        start = {
            # Desenvolvimento
            'development': {
                'app': 'main:app',
                'host': host,
                'port': port,
                'reload': True,
            },  # Produção
            'production': {
                'app': 'main:app',
                'host': host,
                'port': port,
                'reload': False,
            },
        }

        if environment == 'development':
            print('SERVIDOR EM MODO [DESENVOLVIMENTO]')
            uvicorn.run(**start.get('development'))
        else:
            print('SERVIDOR EM MODO [PRODUCAO]')
            uvicorn.run(**start.get('production'))


app = Main().app


def main():
    server = Main()
    server.run()
