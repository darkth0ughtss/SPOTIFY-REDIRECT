from flask import Flask, request
from pymongo import MongoClient
from spotipy.oauth2 import SpotifyOAuth
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Environment variables for MongoDB and Spotify credentials
MONGO_URL = os.environ.get('MONGO_URL')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI')

if not all([MONGO_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI]):
    raise EnvironmentError("Required environment variables are missing")

mongo_client = MongoClient(MONGO_URL)
db = mongo_client["spotify_bot"]
users_collection = db["users"]

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-currently-playing"
)

@app.route('/')
def index():
    return "Heroku Flask App is running."

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return "Missing code in callback", 400

    try:
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            user_id = state
            users_collection.update_one(
                {"user_id": int(user_id)},
                {"$set": {"access_token": token_info["access_token"], "refresh_token": token_info["refresh_token"]}},
                upsert=True
            )
            return "You have successfully logged in to Spotify! You can return to Telegram now."
    except Exception as e:
        logging.error(f"Error during OAuth callback: {e}")
        return f"Failed to get the token: {e}", 400

    return "Failed to get the token", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
