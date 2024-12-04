FROM python:3.9-slim

# Instalar dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalar bibliotecas Python
RUN pip install --no-cache-dir ultralytics opencv-python pyJWT requests

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o script e arquivos necessários para o container
COPY fire_detection.py .
COPY best.pt .

# Executar o fire_detection
CMD ["python", "fire_detection.py"]
