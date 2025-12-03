import requests
from bs4 import BeautifulSoup
import os
import subprocess

URL = "https://www.irekia.euskadi.eus/es/tags/plenoordinario?uid=5252"
DOWNLOAD_DIR = "videos"
AUDIO_DIR = "audios"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

# 1. Descargar página
html = requests.get(URL).text
soup = BeautifulSoup(html, "html.parser")

# 2. Buscar enlaces a videos (mp4)
video_urls = set()
for tag in soup.find_all(["video", "source"]):
    src = tag.get("src")
    if src and src.endswith(".mp4"):
        if src.startswith("/"):
            src = "https://www.irekia.euskadi.eus" + src
        video_urls.add(src)

print("Encontrados:", len(video_urls), "videos")

# # 3. Descargar cada video
# for url in video_urls:
#     filename = url.split("/")[-1]
#     path = os.path.join(DOWNLOAD_DIR, filename)

#     if not os.path.exists(path):  # evitar descargas repetidas
#         print("Descargando:", filename)
#         with requests.get(url, stream=True) as r:
#             with open(path, "wb") as f:
#                 for chunk in r.iter_content(chunk_size=8192):
#                     f.write(chunk)

#     # 4. Convertir a audio (mp3)
#     audio_file = os.path.join(AUDIO_DIR, filename.replace(".mp4", ".mp3"))
#     if not os.path.exists(audio_file):
#         print("Convirtiendo a audio:", audio_file)
#         subprocess.run([
#             "ffmpeg", "-i", path, "-vn", "-acodec", "libmp3lame", "-q:a", "3", audio_file
#         ])

# print("Proceso terminado.")