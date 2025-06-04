# 🎧 Spotify Playlist Downloader (via CSV) - Dockerized

Este proyecto permite descargar canciones desde YouTube en formato MP3, basándose en una playlist exportada de Spotify como archivo CSV. Incluye conversión automática a MP3, metadatos básicos, registro en base de datos y ejecución automatizada dentro de Docker.

## 🚀 Características

- 🐳 Ejecutable completamente en Docker (ideal para Windows con Docker Desktop)
- 🎵 Descarga de audio desde YouTube (con [`yt-dlp`](https://github.com/yt-dlp/yt-dlp))
- 🔁 Evita canciones repetidas (verifica por ISRC o nombre normalizado)
- 📁 Guarda las canciones en una carpeta local compartida con el contenedor
- 🧠 Almacena los resultados en una base de datos SQLite
- 🎯 Conversión automática a MP3 (con `ffmpeg`)
- 🏷️ Asigna metadatos básicos (track, artista, álbum)

---

## 📁 Estructura de Carpetas
├── data/

│ ├── playlist.csv # CSV exportado desde TuneMyMusic o Spotify

│ └── spotify_downloads.db # Base de datos SQLite (se crea automáticamente)

├── music/ # Carpeta donde se guardan los archivos MP3

├── docker-compose.yml

├── Dockerfile

├── requirements.txt

└── spotify_downloader.py


---

## 🛠️ Requisitos

- Docker Desktop en Windows ([instalar aquí](https://docs.docker.com/desktop/install/windows-install/))
- El archivo `playlist.csv` exportado desde tu playlist de Spotify (usa [TuneMyMusic](https://www.tunemymusic.com/))
- Tener configuradas las carpetas `data/` y `music/` en tu proyecto

---

## ▶️ Cómo usar

1. **Clona el repositorio:**

  bash
    git clone https://github.com/tuusuario/spotify-downloader.git
    cd spotify-downloader

2. Agrega tu archivo playlist.csv dentro de la carpeta data/.

  Debe tener las columnas:
  Track name,Artist name,Album,Playlist name,Type,ISRC,Spotify - id

3. Construye la imagen:
  docker-compose build

4. Ejecuta la descarga:
  docker-compose up

Los archivos MP3 se descargarán en la carpeta music/.

💡 Notas importantes
- Evita duplicados: El script verifica por ISRC, y si no existe, por el nombre del track y artista normalizado.
- Conversión a MP3: Asegúrate de que ffmpeg esté instalado dentro del contenedor (ya incluido en la imagen).
- Docker Volumes: La carpeta music/ se monta como volumen, por lo que los MP3 permanecen fuera del contenedor.
- Descargas fallidas: Se registran con estado "error" en la base de datos SQLite.

🧱 Construir imagen personalizada (opcional)
Para subir esta herramienta a tu Docker Hub:
  docker build -t tuusuario/spotify-downloader .
  docker push tuusuario/spotify-downloader

🧾 Licencia
MIT License — uso libre para aprendizaje o uso personal.

🙋 Autor
Creado por Iván Guzmán como proyecto personal de aprendizaje y automatización.
