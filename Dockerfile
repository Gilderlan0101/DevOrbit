# Usando a imagem oficial do Python como base
FROM python:3.8-slim

# Definindo o diretório de trabalho no container
WORKDIR /application

# Copiando o arquivo de dependências (requirements.txt) para dentro do container
COPY requirementes.txt /application/

# Instalando as dependências
RUN pip install --no-cache-dir -r requirementes.txt

# Copiando todos os arquivos do seu projeto para dentro do container
COPY . /application/

# Definindo a variável de ambiente para evitar a criação de arquivos pyc
ENV PYTHONUNBUFFERED=1


# Expondo a porta 5000 para a aplicação Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "run.py"]
