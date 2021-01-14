from requests_oauthlib import OAuth2Session

from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from flask.json import jsonify
import json
import os

app = Flask(__name__)

#OAuth Variables
client_id = '28bf5c72de76f94a5fb1d9454e347d4e'
#Sanbox/test env so okay to store secret in repo but in production, wouldn't include actual secret value within repo
client_secret = '3e9f2e9716dba6ec74a2e42e90974828'
#Production should use https, below for POC
redirect_uri = 'http://3.140.199.135/callback'
authorization_base_url = 'https://api.id.me/oauth/authorize'
token_url = 'https://api.id.me/oauth/token'
attributes_url = 'https://api.id.me/api/public/v3/attributes.json'
scope = ['login']

#In production, would remove and config SSL certs/apache/ec2 etc to allow for https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.urandom(24)

@app.route('/')

def demo():
    return render_template('index.html')

@app.route("/callback", methods=["GET"])
def callback():
    # Exchange your code for an access token
    idme  = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = idme.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    # At this point you can fetch a user's attributes but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))

@app.route("/profile", methods=["GET"])
def profile():
    # Fetching the user's attributes using an OAuth 2 token.
    idme = OAuth2Session(client_id, token=session['oauth_token'])
    payload = idme.get(attributes_url).json()

    session['profile'] = 'true'
    json_payload = jsonify(payload)
    req_data = json_payload.get_json()
    #Should include if statements with ['attributes']['handle'] for these in case order of the array changes down the line
    email = req_data['attributes'][0]['value']
    first_name = req_data['attributes'][1]['value']
    last_name = req_data['attributes'][2]['value']
    return '''
        Thank you {} {}!
        Your status has been verified with ID.me using the following email address:
        {}'''.format(first_name, last_name, email)
