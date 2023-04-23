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

    # Select random champ from mains_names list, format and store
    champion = mains_names[random.randint(0, len(mains_names)-1)]
    champion = format_name(champion)

    # Open file with information about that specific champ
    with open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{champion}.json") as file:
        skins_list = [] 
        names = []

        # Load data into list of dictionaries, trim into only skins for that champ
        data = json.load(file)
        skins = data["data"][champion]["skins"]

        # Select 4 random skins from list
        samples = random.sample(range(1, len(skins)-1), 4)
        for sample in samples:
            skin = skins[sample]
            skins_list.append(skin)

        # Append their names and the id for the first one (will be the right one)
        for elem in skins_list:
            names.append(elem["name"])
        image_id = (skins_list[0]["num"])

        #Return champion name, list of skin names and id to look for the question's image. Correct answer will be names[0]

    return champion, names, image_id



def generate_question_spell_name(mains_names):
    # Function to generate question of the "What is the name of this ability" kind

    # Select random champ from mains_names list, format and store
    champion = mains_names[random.randint(0, len(mains_names)-1)]
    champion = format_name(champion)

    # Open file with information about that specific champ
    with open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{champion}.json") as file:
        names = []
        data = json.load(file)
        spells = data["data"][champion]["spells"]
        num = random.randint(0,3)
        # Id list for image
        image_id = spells[num]["id"]

        # Spell name for answers
        for spell in spells:
            names.append(spell["name"])

        return champion, names, image_id

        print(id)
        print(name_list)




