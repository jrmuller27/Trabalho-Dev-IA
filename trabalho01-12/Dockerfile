# Dockerfile

# 1. IMAGEM BASE: Escolhemos uma imagem oficial do Python 3.10 otimizada (slim).
FROM python:3.10-slim

# 2. DIRETÓRIO DE TRABALHO: Define onde o código estará dentro do container.
WORKDIR /app

# 3. COPIAR DEPENDÊNCIAS: Copia o arquivo que lista as bibliotecas do Python.
# Lembre-se: requirements.txt deve ter sido criado com 'pip freeze > requirements.txt' no seu venv.
COPY requirements.txt .

# 4. INSTALAR DEPENDÊNCIAS: Instala todas as bibliotecas necessárias.
# O '--no-cache-dir' economiza espaço no container.
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPIAR PROJETO: Copia todo o conteúdo da pasta raiz (código, modelos, dados) para o container.
# Isso garante que as pastas 'src/', 'models/' e 'data/' estejam presentes.
COPY . /app

# 6. EXPOR PORTA: Informa ao Docker que o serviço será executado na porta 8000.
EXPOSE 8000

# 7. COMANDO DE EXECUÇÃO: Define o comando que será executado quando o container for iniciado.
# '0.0.0.0' é crucial para que o container seja acessível de fora.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]