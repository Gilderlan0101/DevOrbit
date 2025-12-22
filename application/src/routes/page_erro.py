from flask import Blueprint
from flask_login import login_required
from dotenv import load_dotenv


"""
Esta rota é exibida sempre que ocorre um erro HTTP ou HTTPS, e redireciona o usuário para o feed da plataforma após uma breve mensagem de erro.
Este é um exemplo de como estamos trabalhando para garantir que a experiência na DevOrbit seja fluida e sem interrupções!
"""

load_dotenv()
erro_http_ = Blueprint('errorHttp', __name__, template_folder='templates')


@erro_http_.route('/devorbit/erro_http/')
@login_required
def page_erro():

    # Renderiza uma página com a mensagem antes de redirecionar
    return """
    <html>
        <body>
            <p>Erro HTTP ou HTTPS: Você precisa incluir métodos válidos. Você está sendo redirecionado...</p>
            <script>
                setTimeout(function() {
                    window.location.href = '/devorbit/feed/';
                }, 3000);  // 3 segundos antes do redirecionamento
            </script>
        </body>
    </html>
    """
