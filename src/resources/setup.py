from flask import Flask, request
import json
import bcrypt
from __main__ import app
from tools import discord_crud
import os
from base64 import b64encode
import requests

HEADERS = discord_crud.HEADERS
BASE_URL = discord_crud.BASE_URL
USERS_CHANNEL_ID = discord_crud.USERS_CHANNEL_ID

@app.route("/setup", methods=["POST"])
def setup():
    # check if channel already exists, if it doesn't return a 409 conflict
    channel = discord_crud.get_channel(USERS_CHANNEL_ID)
    if channel.status_code != 200:
        return { "status": "error", "message": "Users channel does not exist" }, 409
    
    # check if channel is empty, if it isn't return a 409 conflict
    parameters = { "limit": 1 }
    messages = requests.get(f'{BASE_URL}/channels/{USERS_CHANNEL_ID}/messages', params=parameters, headers=HEADERS)
    if len(messages.json()) != 0:
        return { "status": "error", "message": "Users channel is not empty" }, 409
    
    # get user and password from request
    try:
        request_body = json.loads(request.data, strict=False)
        user = request_body["user"]
        pwd = request_body["pwd"]
        assert(type(user) == str and type(pwd) == str)
        assert(len(user) > 0 and len(pwd) > 0)
    except:
        return { "status" : "error", "message": "Invalid request body " }, 400
        
    # create user
    pwd_hash = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_data = { "user": user, "pwd": pwd_hash, "admin": True }
    discord_crud.send_message(USERS_CHANNEL_ID, json.dumps(user_data))

    # below doesnt work bc send_message needs to return the response, we can change that later
    # discord_response = discord_crud.send_message(USERS_CHANNEL_ID, json.dumps(user_data))
    # if discord_response.status_code != 200:
    #     return { "status": "error", "message": "Failed to send message to users channel" }, 500
    
    # return success
    return { " status": "success", "message": "User created" }, 200