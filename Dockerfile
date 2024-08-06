# Use uma imagem base do Python
FROM python:3.10-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie os arquivos de requisitos
COPY requirements.txt requirements.txt

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho
COPY . .

# Defina a variável de ambiente para que a Flask saiba que está em produção
ENV FLASK_ENV=production

# Exponha a porta em que a aplicação Flask vai rodar
EXPOSE 8080

# Comando para rodar o servidor usando Waitress
CMD ["python", "start_server.py"]
