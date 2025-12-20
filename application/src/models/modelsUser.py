class Cadastro:
    """
    Representa as informações iniciais do cadastro de um usuário.

    Esta classe é responsável por armazenar as informações essenciais
    para o cadastro de um usuário, incluindo nome, sobrenome, email,
    idade e senha. As verificações mais profundas, como validação de
    formato de email ou a força da senha, serão feitas em etapas posteriores.

    Atributos:
        name (str): O nome do usuário. Será capitalizado automaticamente.
        last_name (str): O sobrenome do usuário.
        email (str): O email do usuário. Espera-se que seja um email válido.
        age (int): A idade do usuário. Pode ser usada para validação de
            maioridade.
        password (str): A senha do usuário. No futuro, será importante realizar
                        validações e criptografia.
    """

    def __init__(
        self, name: str, last_name: str, email: str, age: int, password: str
    ):
        self.name = name.capitalize()  # Capitaliza o primeiro nome
        self.last_name = last_name
        self.email = email
        self.age = age
        self.password = password


class UserInformation:
    """
    Contém as informações de um usuário após o cadastro.

    Esta classe armazena as informações de perfil de um usuário, como
    o nome de usuário, nome completo, email e ocupação. Ela serve como
    um modelo para o armazenamento de dados de usuários no sistema e
    poderá ser utilizada para exibir ou editar dados do perfil do usuário.

    Atributos:
        username (str): O nome de usuário único escolhido pelo usuário.
        name (str): O nome completo do usuário.
        email (str): O email do usuário. Geralmente único e utilizado para
            login.
        occupation (str): A ocupação ou profissão do usuário. Pode ser útil
                           para categorizar usuários.
    """

    def __init__(self, username, name, email, occupation):
        self.username = username
        self.name = name
        self.email = email
        self.occupation = occupation


class Login:
    """
    Representa os dados necessários para realizar o login de um usuário.

    A classe Login é usada para armazenar as credenciais de login, como
    o email e a senha. Esse modelo servirá para autenticação do usuário
    durante o processo de login. As verificações de autenticação e a segurança
    serão realizadas em etapas posteriores.

    Atributos:
        email (str): O email do usuário, usado para identificar o
            usuário no sistema.
        password (str): A senha do usuário, que será verificada durante o
            processo de login.
    """

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


class Links:
    """
    Contém os links de redes sociais ou sites de um usuário.

    Esta classe armazena os links de redes sociais e sites associados
    ao perfil do usuário. Ela pode ser expandida para incluir mais links
    à medida que o sistema exige. Para verificar se os links são válidos
    (ex: validar o formato de URLs), verificações adicionais serão feitas
    em etapas posteriores.

    Atributos:
        github (str, optional): Link para o perfil do GitHub do usuário.
        likedin (str, optional): Link para o perfil do LinkedIn do usuário.
        site (str, optional): Link para o site pessoal ou portfólio do usuário.
    """

    def __init__(self, github=None, linkedin=None, site=None):
        self.github = github
        self.linkedin = linkedin
        self.site = site