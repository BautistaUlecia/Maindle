import os
import requests
from flask import redirect, render_template, request, session
from functools import wraps
import json
from api_key import key
import random


def lookup(summoner, region):
    # Uses riot api to get summoner ID
    try:
        api_key = key()
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
    api_key = key()
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
    
def format_name(name):
    name = name.replace(" ", "")
    if "'" in name:
        name = name.replace("'", "")
        name = name.capitalize()
    return name


def generate_question_skin_name(mains_names):
    # Function to generate question of the "What is the name of this skin" kind
    question = ""
    answer = ""
    champion = mains_names[random.randint(0, len(mains_names)-1)]
    champion = format_name(champion)
    print (champion)
    with open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{champion}.json") as file:
        skins_list = []
        names = []
        data = json.load(file)
        skins = data["data"][champion]["skins"]
        #print(skins) # lista de skins para el champ
        for x in range (0,4):
            skin = skins[random.randint(1, len(skins)-1)]
            skins_list.append(skin)
        print(skins_list) # 4 skins random para el champ
        for elem in skins_list:
            names.append(elem["name"])
        image_id = (skins_list[0]["num"])
        
        
        print(names)
        print(image_id)





    return champion, names, image_id