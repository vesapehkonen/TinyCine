from flask import Flask, render_template, jsonify, send_from_directory
import subprocess
from tinydb import TinyDB, Query
import os
import sys

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "config"))
sys.path.insert(0, CONFIG_PATH)
from config import VIDEO_DIR, POSTER_DIR, MOVIES_TXT, MOVIES_DB, BACKUP_FOLDER, TMDB_API_KEY

app = Flask(__name__)

# Path to the bash script that will run mplayer
BASH_SCRIPT_PATH = os.path.join(os.getcwd(), 'play_video.sh')

# Function to format the movie name (replace underscores with spaces and capitalize words)
def format_movie_name(movie_name):
    words = movie_name.replace('_', ' ').split()
    formatted_name = ' '.join([word.capitalize() for word in words])
    return formatted_name

# Initialize TinyDB
db = TinyDB(MOVIES_DB)

def clean_genre(genre):
    if isinstance(genre, str):
        try:
            # If the genre is a string representing a list (e.g., "['Action', 'Drama']")
            genre_list = json.loads(genre.replace("'", '"'))  # Convert to a valid JSON list
            if isinstance(genre_list, list):
                return ", ".join(g.strip() for g in genre_list)  # Join genres into a clean string
        except json.JSONDecodeError:
            pass  # If it fails, return the original string
    # If the genre is already a list, clean it up
    if isinstance(genre, list):
        return ", ".join(g.strip() for g in genre)
    return genre  # Return as-is if it’s neither a string list nor a regular list

# Function to read movies from TinyDB
def get_movies_list():
    try:
        # Retrieve all movies from the TinyDB database
        movies = db.all()

        filtered_movies = [{
            "id": m.get("id", "Unknown"), 
            "poster": m.get("poster", "default.jpg"), 
            "year": m.get("year", "Unknown"), 
            "name": m.get("name", "Unknown"), 
            "actors": m.get("actors", []), 
            "genre": clean_genre(m.get("genres", [])), 
            "rating": m.get("rating", "N/A")
        } for m in movies if isinstance(m, dict)]
        
        print(filtered_movies)
        # Sort movies by year in descending order (newest to oldest)
        filtered_movies.sort(key=lambda x: x['year'], reverse=True)
        return filtered_movies
    except Exception as e:
        print(f"Error retrieving movies from TinyDB: {e}")
        return []

def get_movie_by_id(movie_id):
    # Replace with your code to fetch movie details by ID from your data
    #movie = fetch_movie_details_from_db_or_api(movie_id)
    query = Query()
    movie = db.get(query.id == movie_id)
    #print(movie)
    # Extract the necessary data
    """
    movie_details = {
        "name": movie['name'],
        "overview": movie.overview,
        "genres": [genre['name'] for genre in movie.genres],
        "director": get_director_name(movie),
        "actors": [actor['name'] for actor in movie.actors],
        "release_date": movie.release_date,
        "poster": movie.poster_path,
        "file_name": movie.file_name,
        "year": movie.year
    }
    return movie_details
    """
    return movie

# Route to serve the poster images
@app.route('/posters/<filename>')
def serve_poster(filename):
    print(f'/posters/{filename}')
    return send_from_directory(POSTER_DIR, filename)

# Route to render the HTML page
@app.route('/')
def index():
    # Get the list of movies from the text file
    movies = get_movies_list()
    return render_template('index.html', movies=movies)

# Route to play a specific video using the bash script
@app.route('/play_video/<path:movie_file>', methods=['GET'])
def play_video(movie_file):
    # Full path to the video file
    video_path = os.path.join(VIDEO_DIR, movie_file)
    print(f'requested video_path={video_path}')
    # Check if the file exists
    if not os.path.exists(video_path):
        return jsonify({"status": "error", "message": f"Video {movie_file} not found."}), 404

    # Run the bash script that launches mplayer in a new terminal window
    try:
        subprocess.Popen([BASH_SCRIPT_PATH, video_path])  # Call the bash script
        return jsonify({"status": "success", "message": f"Playing {movie_file} in a new terminal."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/movie/<movie_id>')
def movie_details(movie_id):
    # Retrieve movie details by movie_id
    movie = get_movie_by_id(movie_id)
    return render_template('movie_detail.html', movie=movie)
    
# Start the Flask app
if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=8000)
    app.run(debug=True, host='localhost', port=8000)

