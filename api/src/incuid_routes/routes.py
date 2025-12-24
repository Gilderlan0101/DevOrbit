# included_routes.py
from src.auth.router import router as auth_or_register
from src.post.router import router as user_actions


def register_all_routes(app):
    """
    Registra todos os APIRouters no aplicativo FastAPI principal.
    """

    # AUTH
    app.include_router(auth_or_register)
    app.include_router(user_actions)


__all__ = ['register_all_routes']
