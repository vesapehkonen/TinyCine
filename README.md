# 🎬 TinyCine

TinyCine is a **personal movie collection manager** built with **TinyDB & TMDb API**.  
It allows you to **search, filter, and organize** your movie database easily.

##  Features
Fetch movie details (title, actors, genres, rating, runtime, etc.) from TMDb  
Store movies locally using TinyDB  
Search & filter movies by name, year, actors, rating, and genre  
Automatic poster fetching  
Simple **Flask-based** web interface  

## Using Git LFS
This repository uses **Git Large File Storage (LFS)** for handling large media files.  
Currently, **only `sample_movie.mp4` is stored using Git LFS**.
If you haven't installed Git LFS yet, please do so before cloning:
```sh
sudo apt install git-lfs
git lfs install
```

##  Installation
### 1. Clone the Repository
```sh
git clone https://github.com/vesapehkonen/TinyCine.git
cd TinyCine
```
Install Dependencies
```sh
pip install -r requirements.txt
```

### 2. Configure the App

Edit config.py to set up:

```sh
VIDEO_DIR = "/path/to/videos"
POSTER_DIR = "/path/to/posters"
MOVIES_TXT = "/path/to/movies.txt"
MOVIES_DB = "/path/to/movies.json"
BACKUP_FOLDER = "/path/to/backups"
TMDB_API_KEY = "your_tmdb_api_key_here"
```
Replace paths with your actual directories.
Get a TMDb API key from TMDb.

## Usage
### 1. Add New Movies
Edit movies.txt and add movies in this format:
```sh
movie_filename.mp4|poster_filename.jpg|Movie Name|Year
```
Then run:
```sh
python scripts/update_db.py
```
This fetches missing movie details and updates movies.json.
### 2. Start the Web Interface

```sh
flask run
```
Now open http://127.0.0.1:5000/ in your browser.

## License
This project is open-source under the MIT License.

