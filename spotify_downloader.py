import os
import sqlite3
import csv
import yt_dlp
from tqdm import tqdm
from time import sleep
import re
import unicodedata
import subprocess
from mutagen.easyid3 import EasyID3

# Configuración de rutas
DATABASE_FILE = "data/spotify_downloads.db"
CSV_FILE = "data/playlist.csv"
MUSIC_FOLDER = "music/"

# Crear base de datos si no existe
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT,
            artist_name TEXT,
            album TEXT,
            isrc TEXT,
            spotify_id TEXT,
            status TEXT,
            downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Leer CSV
def read_csv():
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def normalize_text(text):
    """Normaliza un texto eliminando espacios extra, caracteres especiales y diferencias de mayúsculas/minúsculas."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)  # Normalizar acentos
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar caracteres especiales
    text = re.sub(r'\s+', ' ', text)  # Reemplazar múltiples espacios por uno solo
    return text

def is_downloaded(track, artist, isrc):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    normalized_track = normalize_text(track)
    normalized_artist = normalize_text(artist)

    cursor.execute("""
        SELECT * FROM downloads 
        WHERE (isrc = ? AND status = 'success') 
        OR (LOWER(track_name) = ? AND LOWER(artist_name) = ? AND status = 'success')
    """, (isrc, normalized_track, normalized_artist))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Hook para mostrar progreso en la misma línea
def progress_hook(t):
    def hook(d):
        if d['status'] == 'downloading':
            t.update(float(d['_percent_str'].strip('%')) - t.n)
    return hook

# Descargar canción con yt-dlp
def download_song(track, artist, isrc, album):
    query = f"ytsearch:{track} {artist} audio"
    output_path = os.path.join(MUSIC_FOLDER, f"{track} - {artist}.%(ext)s")
    
    with tqdm(total=100, desc=f"{track[:30]}...", bar_format="{l_bar}{bar} {n:.1f}%", ncols=80) as t:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,  # Usar la extensión .mp3
            'noplaylist': True,
            'quiet': True,
            'progress_hooks': [progress_hook(t)],
            #'postprocessors': [{
            #    'key': 'FFmpegAudioConvertor',  # Asegúrate de que esta clave esté bien escrita
            #    'preferredcodec': 'mp3',  # Convertir el audio a mp3
            #    'preferredquality': '192',  # Calidad 192kbps
            #}]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([query])  # Descargar la canción
                downloaded_file = os.path.join(MUSIC_FOLDER, f"{track} - {artist}.webm")  # Nombre de archivo original
                mp3_file = os.path.join(MUSIC_FOLDER, f"{track} - {artist}.mp3")  # Archivo convertido a mp3

                # Convertir el archivo descargado a MP3 usando ffmpeg
                if os.path.exists(downloaded_file):
                    #subprocess.run(['ffmpeg', '-i', downloaded_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', mp3_file])
                
                    subprocess.run(
                        ['ffmpeg', '-i', downloaded_file, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', mp3_file],
                        stdout=subprocess.DEVNULL
                    )

                    os.remove(downloaded_file)  # Eliminar el archivo original después de convertirlo
                    
                set_metadata(mp3_file, track, artist, album)
                return "success"
            except Exception as e:
                return f"error: {str(e)}"

def set_metadata(mp3_file, track, artist, album):
    try:
        audio = EasyID3(mp3_file)
    except Exception:
        from mutagen.mp3 import MP3
        audiofile = MP3(mp3_file)
        audiofile.add_tags()
        audiofile.save()
        audio = EasyID3(mp3_file)

    audio['title'] = track
    audio['artist'] = artist
    audio['album'] = album
    audio.save()

# Procesar la lista de canciones
def process_playlist():
    playlist = read_csv()
    total_songs = len(playlist)
    downloaded = 0
    skipped = 0
    errors = 0
    
    print("\nProcesando playlist...\n")
    
    with tqdm(total=total_songs, desc="Progreso general", unit="canción", dynamic_ncols=True) as pbar:
        for song in playlist:
            track, artist, isrc, album = song['Track name'], song['Artist name'], song['ISRC'], song['Album']
            
            if is_downloaded(track, artist, isrc):
                tqdm.write(f"Omitida (ya descargada): {track} - {artist}")
                skipped += 1
            else:
                status = download_song(track, artist, isrc, album)
                if status == "success":
                    downloaded += 1
                else:
                    errors += 1

                # Guardar en la base de datos
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO downloads (track_name, artist_name, album, isrc, spotify_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                               (track, artist, album, isrc, song['Spotify - id'], status))
                conn.commit()
                conn.close()
            
            pbar.update(1)
            sleep(0.5)  # Simulación de proceso
    
    # Mostrar estadísticas finales
    print("\n" + "="*40)
    print(f"| Total de canciones: {total_songs:<10}           |")
    print(f"| Descargadas: {downloaded:<10}                   |")
    print(f"| Omitidas: {skipped:<10}                         |")
    print(f"| Errores: {errors:<10}                           |")
    print("="*40 + "\n")

# Ejecutar
if __name__ == "__main__":
    setup_database()
    process_playlist()
    print("Proceso finalizado. Puedes cerrar el programa.")
