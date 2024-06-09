# flask_app.py
from flask import Flask, request, redirect
from pymongo import MongoClient
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)

# Replace these with your MongoDB URI and Spotify credentials
MONGO_URL = "mongodb+srv://darkth0ughtss00:loniko0908@music.njvuzcz.mongodb.net/?retryWrites=true&w=majority&appName=Music"
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["spotify_bot"]
users_collection = db["users"]

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return "Missing code in callback", 400

    token_info = sp_oauth.get_access_token(code)
    if token_info:
        user_id = state
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"access_token": token_info["access_token"], "refresh_token": token_info["refresh_token"]}},
            upsert=True
        )
        return "You have successfully logged in to Spotify! You can return to Telegram now."

    return "Failed to get the token", 400

if __name__ == '__main__':
    app.run(debug=True)
