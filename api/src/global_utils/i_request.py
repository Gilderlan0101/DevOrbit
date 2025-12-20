from fastapi import Request, HTTPException, status

def permitted_origin(request: Request):
    """Verifica a origem da requisição em rotas públicas."""

    # Use 'origin' em vez de 'host'
    origin = request.headers.get('origin')

    # TODO: Adiciona rota para o front end
    allowed_origins = [
        'http://localhost:8000',
    ]

    if origin is None:
        # Para requisições do mesmo origin (mesmo domínio), o cabeçalho origin pode não ser enviado
        # Podemos verificar o referer como fallback
        referer = request.headers.get('referer')
        if referer:
            # Extrair origem do referer
            import re
            match = re.match(r'(https?://[^/]+)', referer)
            if match:
                origin = match.group(1)

        if origin is None:
            # Se ainda for None, podemos permitir se for uma chamada direta da API
            # ou levantar exceção dependendo do seu caso de uso
            host = request.headers.get('host', '')
            if host in ['127.0.0.1:8000', 'localhost:8000']:
                return True

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Origin header required',
            )

    if origin not in allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Origin not allowed',
        )

    return True
