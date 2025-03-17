import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIDEO_DIR = os.path.join(ROOT_DIR, "movies")
POSTER_DIR = os.path.join(ROOT_DIR, "posters")
MOVIES_TXT = os.path.join(ROOT_DIR, "movies.txt")
MOVIES_DB = os.path.join(ROOT_DIR, "movies.json")
BACKUP_FOLDER = os.path.join(ROOT_DIR, "backups")
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
MAX_BACKUPS = 5
