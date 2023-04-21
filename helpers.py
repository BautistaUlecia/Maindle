import os
import requests
from flask import redirect, render_template, request, session
from functools import wraps
import json

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def lookup(summoner, region):
    # Uses riot api to get summoner ID
    try:
        api_key = "RGAPI-3b6ef0f5-f752-4719-8ac2-579b08a206a8"
        summonerName = summoner
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}"
        response = requests.get(url)
    except requests.RequestException:
        return None
    #parse
    try:
        data = response.json()
        return(data["id"])

    except (KeyError, TypeError, ValueError):
        return None

def lookup_champs(id, region):
    # Uses summoner id to get mains from riot API
    mains = []
    api_key = "RGAPI-3b6ef0f5-f752-4719-8ac2-579b08a206a8"
    url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}/top?count=5&api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    for x in data:
        mains.append(x["championId"])
    return mains

def champ_id_to_name(mains_id):
    print(mains_id)
    with open("champion.json", errors="ignore", encoding="utf-8") as file:
        mains_names = []
        data = json.load(file)
        data = data["data"]
        for x in data:
            key = data[x]["key"]
            key = int(key)
            for y in mains_id:
                if key == y:
                    print(data[x]["name"])
                    mains_names.append(data[x]["name"])
        return mains_names

