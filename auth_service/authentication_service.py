from flask import Flask, redirect, request, jsonify
import requests
from urllib.parse import urlencode
from config import CLIENT_ID, CLIENT_SECRET
import flask_monitoringdashboard as dashboard

app = Flask(__name__)
dashboard.config.init_from(file='auth_config.cfg')

PORT = 8000
# REDIRECT_URI = 'http://localhost:5000/callback'                     # use for running locally
REDIRECT_URI = 'http://146.190.166.177:5000/callback'                 # redirect back to client on droplet 
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'user-library-read user-top-read user-read-recently-played user-read-private user-read-email' 


def get_access_token(payload):
    """
    Gets new access token using refresh token.

    :param payload: request arguments
    :return: json of HTTP response
    """
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# responsible for passing out access tokens
@app.route('/authorize')
def authorize():
    url_params = urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPE,
        'redirect_uri': REDIRECT_URI            # redirect to client callback URL
    })

    auth_url = f'{SPOTIFY_AUTH_URL}?{url_params}'
    return jsonify({'auth_url': auth_url})


@app.route('/token', methods=['POST'])
def token():
    payload = request.json
    grant_type = payload.get('grant_type')

    if grant_type == 'authorization_code':
        # authorization code grant type
        payload['client_id'] = CLIENT_ID
        payload['client_secret'] = CLIENT_SECRET
        payload['redirect_uri'] = REDIRECT_URI

    elif grant_type == 'refresh_token':
        # refresh token grant type
        payload['client_id'] = CLIENT_ID
        payload['client_secret'] = CLIENT_SECRET

    else:
        return jsonify({'error': 'Invalid grant type'}), 400

    response_data = get_access_token(payload)

    if response_data:
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Failed to obtain access token'}), 400
    

dashboard.bind(app) # for monitoring dashboard

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=PORT)
