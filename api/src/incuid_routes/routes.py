# included_routes.py
from src.auth.router import router as auth_or_register

def register_all_routes(app):
    """
    Registra todos os APIRouters no aplicativo FastAPI principal.
    """

    # AUTH
    app.include_router(auth_or_register)


__all__ = ['register_all_routes']
