# Documentação Técnica: Sistema de Autenticação JWT com FastAPI e Scopes

## Arquitetura do Sistema

### 1. **Estrutura de Dependências e Injeção**

**`get_current_user`** é uma **dependency** que funciona como um **middleware de autorização** para rotas FastAPI:

```python
async def get_current_user(
    security_scopes: SecurityScopes,           # ← Injetado pelo FastAPI
    token: Annotated[str, Depends(oauth2_scheme)],  # ← Token do header Authorization
) -> SystemUser:
```

### **Mecanismo de Injeção:**
- **`SecurityScopes`**: Contém os scopes exigidos pela rota. Quando você usa `Security(get_current_user, scopes=["email:send"])`, o FastAPI injeta automaticamente este objeto.
- **`oauth2_scheme`**: Extrai o token do header `Authorization: Bearer <token>`.

## 2. **Fluxo de Validação Passo a Passo**

### **Fase 1: Configuração do Header WWW-Authenticate**
```python
authenticate_value = "Bearer"
if security_scopes.scopes:
    authenticate_value = f'Bearer scope={security_scopes.scope_str}'
```
- **Propósito**: Informa ao cliente quais scopes são necessários em caso de erro 401/403.
- **Formato**: `Bearer scope=email:send user:read` para múltiplos scopes.

### **Fase 2: Decodificação JWT**
```python
payload = jwt.decode(token, str(SECRET_KEY), algorithms=ALGORITHM)
```
⚠️ **Ponto Crítico**: Anteriormente havia `algorithms=[str(ALGORITHM)]`, que causava o erro "alg value is not allowed" por converter `"HS256"` para `'"HS256"'` (com aspas extras).

### **Fase 3: Extração de Claims**
```python
username = payload.get("sub")            # Email do usuário (não username!)
scope = payload.get("scope", "")         # String: "email:send user:read"
token_scopes = scope.split()             # Lista: ["email:send", "user:read"]
```

### **Fase 4: Busca do Usuário no Banco**
```python
user = await get_user(db, username=token_data.username)
```
**Importante**: `get_user` busca por **email**, não por username, mesmo que o parâmetro se chame `username`.

### **Fase 5: Verificação de Scopes**
```python
for scope in security_scopes.scopes:
    if scope not in token_data.scopes:
        raise HTTPException(status_code=403, ...)
```
- **Lógica**: Todos os scopes exigidos pela rota DEVEM estar presentes no token.
- **Exemplo**: Rota com `scopes=["email:send"]` → token precisa ter `"email:send"`.

## 3. **Ciclo de Vida do Token**

### **Geração (`create_access_token`):**
```python
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode.update({
        'exp': expire,  # Timestamp com timezone
        "scope": "email:send user:read user:write",  # ← SCOPES AQUI
    })
    return jwt.encode(to_encode, str(SECRET_KEY), algorithm=ALGORITHM)
```

### **Valores Padrão de Scopes:**
- `email:send` → Enviar emails de verificação
- `user:read` → Ler informações do usuário
- `user:write` → Criar/editar recursos

## 4. **Arquivo `utils.py` - Explicação Técnica**

### **`get_user` - Busca Otimizada:**
```python
async def get_user(db, username: str) -> db | None:
    user = await db.filter(email=username).first()
    if not user:  # Ou: if not user or not user.status
        return None
    return user
```
- **Assíncrono**: Usa `await` para não bloquear o event loop.
- **`first()`**: Retorna apenas o primeiro resultado (email é único).

### **`authenticate_user` - Validação Dupla:**
```python
async def authenticate_user(db, username: str, password: str):
    user = await get_user(db=db, username=username)  # 1. Usuário existe?
    if not user:
        return False
    if not verify_password(password, user.password):  # 2. Senha correta?
        return False
    return user
```

### **`verify_password` - Segurança:**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
```
- **Algoritmo**: Usa Argon2 (via `pwdlib.recommended()`), resistente a ataques de força bruta.

## 5. **Códigos de Status HTTP e Significado**

| Código | Significado | Causa Provável |
|--------|-------------|----------------|
| **200** | Sucesso | Token válido e scopes corretos |
| **401 Unauthorized** | Credenciais inválidas | Token expirado, assinatura inválida, usuário não encontrado |
| **403 Forbidden** | Permissão insuficiente | Token não tem os scopes exigidos pela rota |

## 6. **Debug e Logs**

### **Informações Úteis para Debug:**
```python
# Adicione estes prints em get_current_user:
print(f"Token recebido: {token[:50]}...")
print(f"Scopes requeridos: {security_scopes.scopes}")
print(f"Scopes no token: {token_scopes}")
print(f"Usuário buscado: {token_data.username}")
```

### **Sequência de Logs Esperada:**
```
Bearer scope=user:write        # ← Header WWW-Authenticate
['email:send', 'user:read']    # ← Scopes do token (DEBUG)
200 OK                         # ← Sucesso
```

## 7. **Padrões de Uso em Rotas**

### **Rota Pública (sem autenticação):**
```python
@router.get('/public')
async def public_route():
    return {"message": "Acesso livre"}
```

### **Rota Protegida (autenticação básica):**
```python
@router.get('/protected')
async def protected_route(
    current_user: SystemUser = Depends(get_current_user)  # ← Sem scopes
):
    return {"user": current_user.email}
```

### **Rota com Scopes Específicos:**
```python
@router.post('/admin')
async def admin_route(
    current_user: SystemUser = Security(get_current_user, scopes=["admin"])
):
    return {"message": "Acesso administrativo"}
```

### **Rota com Múltiplos Scopes:**
```python
@router.put('/resource/{id}')
async def update_resource(
    current_user: SystemUser = Security(
        get_current_user,
        scopes=["user:read", "user:write"]  # ← AND lógico: precisa de AMBOS
    )
):
    return {"message": "Recurso atualizado"}
```

## 8. **Configuração do Ambiente**

### **Arquivo `.env`:**
```env
SECRET_KEY=uma-chave-secreta-longa-de-pelo-menos-32-caracteres
ALGORITHM=HS256  # ← SEM aspas, apenas HS256
```

### **Importância da `SECRET_KEY`:**
- **32+ caracteres**: Para HS256, mínimo recomendado.
- **Armazenamento seguro**: Nunca commitar no código.
- **Rotação periódica**: Mudar em produção regularmente.

## 9. **Problemas Resolvidos e Soluções**

### **Problema 1: "alg value is not allowed"**
```python
# ERRADO (causava erro):
payload = jwt.decode(token, str(SECRET_KEY), algorithms=[str(ALGORITHM)])

# CORRETO:
payload = jwt.decode(token, str(SECRET_KEY), algorithms=ALGORITHM)
```

### **Problema 2: Scopes ausentes no token**
```python
# Login endpoint - garantir scopes adequados:
access_token = create_access_token(
    data={
        'sub': user.email,
        'scope': "email:send user:read user:write"  # ← Incluir todos necessários
    },
    expires_delta=access_token_expires,
)
```

### **Problema 3: `status=False` bloqueia acesso**
```python
# Em get_user:
if not user or not user.status:  # ← Verifica status
    return None

# Em get_current_user:
if user is None:  # ← Inclui falha por status=False
    raise credentials_exception
```

## 10. **Melhores Práticas Implementadas**

### **1. Timezone Correto:**
```python
# Usa America/Sao_Paulo em vez de UTC
expire = datetime.now(ZoneInfo('America/Sao_Paulo')) + expires_delta
```

### **2. Tratamento de Erros Granular:**
- 401 para problemas de autenticação
- 403 para problemas de autorização
- Mensagens claras no header `WWW-Authenticate`

### **3. Separação de Responsabilidades:**
- `dependencies.py`: Lógica de autorização
- `utils.py`: Operações utilitárias
- `router.py`: Definição de endpoints

### **4. Assincronia Correta:**
```python
# Todas as operações de I/O são async/await
user = await get_user(db, username=token_data.username)
```

## 11. **Exemplo Completo de Requisição/Resposta**

### **Request:**
```http
POST /auth/pull_code_email HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

### **Response (Sucesso):**
```json
{
  "message": "Código enviado com sucesso",
  "User": "joao.silva@example.com"
}
```

### **Response (Erro 403):**
```http
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer scope=user:write
Content-Type: application/json

{
  "detail": "Not enough permissions"
}
```

## 12. **Considerações de Segurança**

### **Token Security:**
- **Vida curta**: 30 minutos (configurável)
- **HTTPS obrigatório**: Em produção
- **HttpOnly cookies**: Alternativa para SPAs

### **Rate Limiting:**
Implementar em rotas de login para prevenir brute force:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
limiter = Limiter(key_func=get_remote_address)
```

### **Logging de Tentativas Falhas:**
```python
import logging
logger = logging.getLogger(__name__)

# Em get_current_user:
except (JWTError, ValidationError) as e:
    logger.warning(f"Token inválido: {e}")
    raise credentials_exception
```

## 13. **Extensibilidade**

### **Adicionar Novos Scopes:**
1. Adicionar em `config.py`:
```python
oauth2_scheme = OAuth2PasswordBearer(
    scopes={
        # ... scopes existentes ...
        "posts:create": "Criar posts",
        "posts:delete": "Excluir posts",
    }
)
```

2. Usar nas rotas:
```python
@router.post('/posts')
async def create_post(
    current_user: SystemUser = Security(get_current_user, scopes=["posts:create"])
):
    # ...
```

Esta documentação técnica cobre todos os aspectos do sistema de autenticação JWT implementado, desde a arquitetura até detalhes de implementação e boas práticas de segurança.
