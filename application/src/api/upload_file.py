import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from flask import jsonify, request, send_from_directory
from flask_restx import Api, Namespace, Resource, fields

load_dotenv()  # Carrega variáveis do arquivo .env

# Caminho onde as imagens serão salvas
caminho_img = 'application/src/static/fotos'  # Diretorio fixo para fotos
os.makedirs(caminho_img, exist_ok=True)

# Namespace para as rotas
api = Namespace('files', description='Operações com arquivos', path='/files')

# Modelos para documentação da API
upload_model = api.model(
    'UploadResponse',
    {
        'filename': fields.String(
            description='Nome do arquivo', example='example.jpg'
        ),
        'content_type': fields.String(
            description='Tipo de conteúdo', example='image/jpeg'
        ),
        'size': fields.Integer(
            description='Tamanho do arquivo em bytes', example=1234
        ),
        'user_id': fields.Integer(
            description='ID do usuário associado', example=1
        ),
    },
)

post_model = api.model(
    'Post',
    {
        'user_id': fields.Integer(required=True, description='ID do usuário'),
        'nome': fields.String(required=True, description='Nome do autor'),
        'titulo': fields.String(required=True, description='Título do post'),
        'post': fields.String(required=True, description='Conteúdo do post'),
    },
)


@api.route('/post/')
class CriandoPostagem(Resource):
    def post(self):
        nome = request.form.get('nome')
        titulo = request.form.get('titulo')
        post_content = request.form.get('post')
        file = request.files.get('file')

        if not nome or not titulo or not post_content:
            return {
                'error': 'Nome, título e conteúdo do post são obrigatórios.'
            }, 400

        img_path = None
        if file:
            ext = os.path.splitext(file.filename)[1]
            img_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            img_path = os.path.join(caminho_img, img_filename)
            file.save(img_path)

        try:
            conn = sqlite3.connect('banco_posts_comunidade.db')
            cursor = conn.cursor()
            data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                """
                INSERT INTO post_do_usuario (nome, data, img_path)
                VALUES (?, ?, ?)
                """,
                (nome, data_atual, img_path),
            )
            conn.commit()
            post_id = cursor.lastrowid
            conn.close()

            response_data = {
                'id': post_id,
                'nome': nome,
                'titulo': titulo,
                'post': post_content,
                'data': data_atual,
                'img_url': f'http://127.0.0.1:5000/files/{os.path.basename(img_path)}'
                if img_path
                else 'https://cdn-icons-png.flaticon.com/512/847/847969.png',
            }

            return jsonify(response_data), 200
        except Exception as e:
            return {'error': f'Erro ao salvar o post: {str(e)}'}, 500


@api.route('/banner/uploadfile/<int:user_id>')
class UploadBanner(Resource):
    def post(self, user_id):
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return 400

        conn = sqlite3.connect(os.getenv('BANCO_DB'))
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if user is None:
            conn.close()
            return {'error': 'Usuário não encontrado'}, 404

        # Define o nome e caminho relativo do arquivo
        ext = os.path.splitext(uploaded_file.filename)[1]
        banner_filename = (
            f"banner_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        )
        relative_file_path = os.path.join(
            'fotos', banner_filename
        )  # Exemplo: fotos/banner_userid_timestamp.png

        # Caminho absoluto para salvar o arquivo fisicamente
        banner_path = os.path.join(caminho_img, banner_filename)
        uploaded_file.save(banner_path)

        # Atualiza o caminho relativo no banco de dados
        cursor.execute(
            'UPDATE usuarios SET banner = ? WHERE id = ?',
            (relative_file_path, user_id),
        )
        conn.commit()
        conn.close()

        return {
            'filename': banner_filename,
            'content_type': uploaded_file.content_type,
            'size': os.path.getsize(banner_path),
            'user_id': user_id,
            'banner_url': f'http://127.0.0.1:5000/files/{banner_filename}',
        }, 200


@api.route('/<int:user_id>', endpoint='get_file')
class GetFile(Resource):
    def get(self, user_id):
        conn = sqlite3.connect(os.getenv('BANCO_DB'))
        cursor = conn.cursor()

        cursor.execute('SELECT photo FROM usuarios WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user is None or user[0] is None:
            return (
                jsonify(
                    {
                        'img_url': 'https://cdn-icons-png.flaticon.com/512/847/847969.png'
                    }
                ),
                200,
            )

        relative_file_path = user[0]
        absolute_file_path = os.path.join(caminho_img, relative_file_path)

        if not os.path.exists(absolute_file_path):
            return {'error': 'Arquivo não encontrado'}, 404

        return send_from_directory(caminho_img, relative_file_path)


@api.route('/uploadfile/<int:user_id>')  # Aqui o tipo int é explicitado
class UploadFile(Resource):
    @api.expect(
        api.parser().add_argument('file', type='file', location='files')
    )
    @api.response(200, 'Success', upload_model)
    def post(self, user_id):
        """
        Realiza o upload de um arquivo e associa ao usuário pelo ID.
        """

        uploaded_file = request.files.get('file')

        # Verifica se o arquivo foi enviado
        if not uploaded_file:
            return {'error': 'Nenhum arquivo enviado'}, 400

        # Conectar ao banco e verificar se o usuário existe
        conn = sqlite3.connect(os.getenv('BANCO_DB'))
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM usuarios WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if user is None:
            conn.close()
            return {'error': 'Usuário não encontrado'}, 404

        # Define o caminho relativo da imagem
        relative_file_path = os.path.join(
            'fotos', uploaded_file.filename
        )  # Ex: 'fotos/foto.jpg'

        # Salva o caminho relativo no banco de dados
        cursor.execute(
            'UPDATE usuarios SET photo = ? WHERE id = ?',
            (relative_file_path, user_id),
        )
        conn.commit()

        # Salva o arquivo no diretório de uploads
        file_path = os.path.join(caminho_img, uploaded_file.filename)
        uploaded_file.save(file_path)

        conn.close()
        print('200')
        return {
            'filename': uploaded_file.filename,
            'content_type': uploaded_file.content_type,
            'size': os.path.getsize(file_path),
            'user_id': user_id,
        }, 200


def register_file_routes(api_instance: Api):
    api_instance.add_namespace(api)
