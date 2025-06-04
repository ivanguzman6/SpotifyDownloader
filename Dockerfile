FROM python:3.11

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos del proyecto
COPY . .

# Crear los directorios de datos y música
RUN mkdir -p /app/data /app/music

# Comando por defecto para ejecutar el script
CMD ["python", "spotify_downloader.py"]