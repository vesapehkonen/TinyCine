import os
import json
from tinydb import TinyDB, Query
from tmdbv3api import TMDb, Movie
import uuid
import urllib
import requests
import datetime
import shutil
import sys

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
sys.path.insert(0, CONFIG_PATH)
from config import MOVIES_TXT, MOVIES_DB, BACKUP_FOLDER, TMDB_API_KEY, MAX_BACKUPS

# ✅ TMDb API Configuration
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie_api = Movie()
BASE_URL = 'https://api.themoviedb.org/3'
POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w200'  # Use 'w200' for smaller images

# ✅ Initialize TinyDB
db = TinyDB(MOVIES_DB)

def create_backup():
    """Creates a timestamped backup of movies.json before modifying it."""
    
    # Ensure the backup folder exists
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    # Generate timestamped backup filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"movies_backup_{timestamp}.json"
    backup_path = os.path.join(BACKUP_FOLDER, backup_filename)

    # Copy movies.json to backup location
    shutil.copy(MOVIES_DB, backup_path)
    print(f"🛠️ Backup created: {backup_path}")

    # 🔹 Cleanup: Keep only the latest `MAX_BACKUPS`
    cleanup_old_backups()

def cleanup_old_backups():
    """Deletes older backups, keeping only the last MAX_BACKUPS."""
    
    backup_files = sorted(
        [f for f in os.listdir(BACKUP_FOLDER) if f.startswith("movies_backup_") and f.endswith(".json")],
        reverse=True  # Sort newest first
    )

    if len(backup_files) > MAX_BACKUPS:
        for old_backup in backup_files[MAX_BACKUPS:]:  # Remove extras
            os.remove(os.path.join(BACKUP_FOLDER, old_backup))
            print(f"🗑️ Deleted old backup: {old_backup}")

def movie_exists(name, year):
    """
    Check if a movie with the given name and year exists in TinyDB.
    """
    MovieQuery = Query()
    return db.search((MovieQuery.name == name) & (MovieQuery.year == year))

def get_movie_poster(movie_name, poster_filename, year=None):
    """Fetch the poster for a movie from TMDb API and save it locally."""
    print(f"🔍 Searching poster for: {movie_name}")

    movie_name_encoded = urllib.parse.quote(movie_name)
    search_url = f"{BASE_URL}/search/movie?api_key={tmdb.api_key}&query={movie_name_encoded}"
    if year:
        search_url += f"&year={year}"

    response = requests.get(search_url)
    data = response.json()

    if data.get('results'):
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            poster_url = f"{POSTER_BASE_URL}{poster_path}"
            img_data = requests.get(poster_url).content
            poster_filepath = os.path.join(POSTER_DIR, poster_filename)

            with open(poster_filepath, 'wb') as f:
                f.write(img_data)
            print(f"✅ Downloaded poster: {poster_filepath}")
        else:
            print(f"❌ No poster found for {movie_name}.")
    else:
        print(f"❌ No results found for {movie_name}.")

def fetch_movie_details(movie_file, poster_file, movie_name, movie_year):
    """
    Fetch movie details from TMDb API.
    """
    try:
        search_results = movie_api.search(movie_name)
        found_movie = None
        for result in search_results:
            if str(result.release_date)[:4] == str(movie_year):
                found_movie = result
                break

        if not found_movie:
            print(f"❌ No movie found for '{movie_name} ({movie_year})'. Skipping.")
            return None

        # Fetch detailed movie info
        movie_details = movie_api.details(found_movie.id)
        movie_details = movie_details['_json']

        # Fetch credits separately
        credits = movie_api.credits(found_movie.id)
        credits = credits['_json']
        cast_list = credits['cast']
        crew_list = credits['crew']
            
        # Extract required fields
        release_date = movie_details.get('release_date', 'Unknown')
        genres = [genre['name'] for genre in movie_details.get('genres', [])]
        runtime = movie_details.get('runtime', 0)
        budget = movie_details.get('budget', 0)
        revenue = movie_details.get('revenue', 0)
        overview = movie_details.get('overview', 'No overview available')
        rating = movie_details.get('vote_average', 0)
            
        actors = [actor['name'] for actor in cast_list[:5]]
        directors = [person['name'] for person in crew_list if person['job'] == 'Director']
        writers = [person['name'] for person in crew_list if person['job'] == 'Original Film Writer']
        producers = [person['name'] for person in crew_list if person['job'] == 'Producer']

        # Extract required details
        return {
            'id': str(uuid.uuid4()),
            'file_name': movie_file,
            'poster': poster_file,
            'name': movie_name,
            'year': movie_year,
            'release_date': release_date,
            'genres': genres,
            'runtime': runtime,
            'budget': budget,
            'revenue': revenue,
            'overview': overview,
            'actors': actors,
            'directors': directors,
            'writers': writers,
            'producers': producers,
            'rating': rating
        }

    except Exception as e:
        print(f"❌ Error fetching details for {movie_name} ({movie_year}): {e}")
        return None

def update_database():
    """
    Reads movies.txt, checks which movies are missing in TinyDB, and updates the database.
    """
    if not os.path.exists(MOVIES_TXT):
        print(f"❌ Error: {MOVIES_TXT} not found!")
        return

    create_backup()
    
    # Read movies.txt
    with open(MOVIES_TXT, "r", encoding="utf-8") as file:
        lines = file.readlines()

    new_movies = []

    # Process each line in movies.txt
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue  # Skip empty or incorrectly formatted lines

        video_file, poster_file, movie_name, movie_year = line.split("|")
        movie_year = int(movie_year)  # Convert year to integer

        # Check if movie is already in TinyDB
        if movie_exists(movie_name, movie_year):
            print(f"✅ {movie_name} ({movie_year}) already exists in database.")
            continue  # Skip existing movies

        # Movie is missing, ask user if they want to fetch details
        user_input = input(f"❓ Fetch details for '{movie_name} ({movie_year})'? (y/n): ").strip().lower()
        if user_input == "y":
            get_movie_poster(movie_name, poster_file, movie_year)
            movie_details = fetch_movie_details(video_file, poster_file, movie_name, movie_year)
            if movie_details:
                # Add video & poster filenames manually since TMDb does not have them
                db.insert(movie_details)  # Add to TinyDB
                print(f"✅ Added {movie_name} ({movie_year}) to database.")
                new_movies.append(movie_details)
            else:
                print(f"❌ Skipping {movie_name} ({movie_year}).")

    # Summary
    if new_movies:
        print(f"\n✅ {len(new_movies)} new movies added to the database.")
    else:
        print("\n✅ No new movies added.")

if __name__ == "__main__":
    update_database()
