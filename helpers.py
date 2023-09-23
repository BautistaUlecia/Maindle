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
    try:
        data = response.json()
        return(data["id"])

    except (KeyError, TypeError, ValueError):
        return None

def lookup_champs(id, region):
    # Uses summoner id to get mains from riot API
    # Some scuffed documentation i used to figure this out
    # https://developer.riotgames.com/apis#champion-mastery-v4
    mains = []
    mastery = []
    api_key = key()
    url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}/top?count=5&api_key={api_key}"
    response = requests.get(url)
    data = response.json()

    # Data returns dictionary, store only championid
    for x in data:
        mains.append(x["championId"])
        mastery.append(x["championPoints"])
    return mains, mastery

def champ_id_to_name(mains_id):
    # Champion.json contains cross-reference between id and name
    with open("static\\dragontail\\13.8.1\\data\\en_US\\champion.json", errors="ignore", encoding="utf-8") as file:
        mains_names = []
        champions = json.load(file)
        data = champions["data"]
        
        # If here data stores all info for all champs. index by id, if they match mains_id, store name.
        for x in data:
            key = data[x]["key"]
            key = int(key)
            for y in mains_id:
                if key == y:
                    mains_names.append(data[x]["name"])
        return mains_names
    
def format_name(name):
    # Takes care of inconsistent name formatting inside riot's database
    if name == "K'Sante":
        return "KSante"
    if name == "Kog'Maw":
        return "KogMaw"
    if name == "Rek'Sai":
        return "RekSai"
    if name == "Wukong":
        return "MonkeyKing"
    if name== "LeBlanc":
        return "Leblanc"
    
    name = name.replace(" ", "")
    if "'" in name:
        name = name.replace("'", "")
        name = name.capitalize()
    return name


def generate_question_skin_name(mains_names):
    # Function to generate question of the "What is the name of this skin" kind

    skins = []
    skins_list = [] 
    names = []

    # Select one random champ from mains_names list, format and store
    champion = mains_names[random.randint(0, len(mains_names)-1)]
    champion = format_name(champion)

    # Load JSON for that specific champ, get data for skins into "skins"
    file = open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{champion}.json" , errors="ignore", encoding="utf-8")
    data = json.load(file)
    skins = data["data"][champion]["skins"]

    # Check that function never returns a champion with less than 4 skins (check 5 because first element is default skin)
    while (len(skins) < 5):
        file.close()
        skins = []
        champion = mains_names[random.randint(0, len(mains_names)-1)]
        champion = format_name(champion)
        print(champion)
        file = open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{champion}.json" , errors="ignore", encoding="utf-8")
        data = json.load(file)
        skins = data["data"][champion]["skins"]
        print(skins)

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

        # Spell name for answers, correct answer will be names[num]
        for spell in spells:
            names.append(spell["name"])

        return num, names, image_id
    
# Horrible function i wrote because riot games doesn't give a list of abilities. had to make my own parsing data, thought it was interesting to add.
""" def get_ability_names():
    formatted_list = []
    names = []
    mains_names=["Aatrox","Akshan","Renata","Vex","Zeri","Bel'Veth","Nilah","K'Sante","Milio","Ahri","Akali","Alistar","Amumu","Anivia","Annie","Aphelios","Ashe","Aurelion Sol","Azir","Bard","Blitzcrank","Brand","Braum","Caitlyn","Camille","Cassiopeia","Cho'Gath","Corki","Darius","Diana","Dr Mundo","Draven","Ekko","Elise","Evelynn","Ezreal","Fiddlesticks","Fiora","Fizz","Galio","Gangplank","Garen","Gnar","Gragas","Graves","Gwen","Hecarim","Heimerdinger","Illaoi","Irelia","Ivern","Janna","Jarvan IV","Jax","Jayce","Jhin","Jinx","Kaisa","Kalista","Karma","Karthus","Kassadin","Katarina","Kayle","Kayn","Kennen","Kha'Zix","Kindred","Kled","Kog'Maw","Leblanc","Lee Sin","Leona","Lillia","Lissandra","Lucian","Lulu","Lux","Malphite","Malzahar","Maokai","Master Yi","Miss Fortune","Mordekaiser","Morgana","Nami","Nasus","Nautilus","Neeko","Nidalee","Nocturne","Nunu","Olaf","Orianna","Ornn","Pantheon","Poppy","Pyke","Qiyana","Quinn","Rakan","Rammus","Rek'Sai","Rell","Renekton","Rengar","Riven","Rumble","Ryze","Samira","Sejuani","Senna","Seraphine","Sett","Shaco","Shen","Shyvana","Singed","Sion","Sivir","Skarner","Sona","Soraka","Swain","Sylas","Syndra","Tahm Kench","Taliyah","Talon","Taric","Teemo","Thresh","Tristana","Trundle","Tryndamere","Twisted Fate","Twitch","Udyr","Urgot","Varus","Vayne","Veigar","Vel'Koz","Vi","Viktor","Vladimir","Volibear","Warwick","Wukong","Xayah","Xerath","Xin Zhao","Yasuo","Yone","Yorick","Yuumi","Zac","Zed","Ziggs","Zilean","Zoe","Zyra"]
    for main in mains_names:
        formatted = format_name(main)
        formatted_list.append(formatted)

    for name in formatted_list:
        with open (f"static\\dragontail\\13.8.1\\data\\en_US\\champion\\{name}.json", encoding="utf8") as asd:
            data = json.load(asd)
            spells = data["data"][name]["spells"]
            for spell in spells:
                names.append(spell["name"])
    return names """

def generate_question_mastery(ids, mastery):
    num = random.randint(0,4)
    id = []
    id.append(ids[num])
    name = champ_id_to_name(id)
    #print(name)
    #print(mastery[num])

    # Roll to see if question is about more or less mastery than
    roll = random.randint(1,2)
    if (roll == 1):
        question_upper = int((mastery[num] * 160) / 100)
        #print(question_upper)
        question_lower = int((mastery[num] * 135) / 100)
        #print(question_lower)
        question = random.randint(question_lower, question_upper)
        #print(question)
    else:
        question_upper = int((mastery[num] * 85) / 100)
        #print(question_upper)
        question_lower = int((mastery[num] * 50) / 100)
        #print(question_lower)
        question = random.randint(question_lower, question_upper)
        #print(question)


    return mastery[num], question, roll, name[0]

def compute_score():
    if (session["user_answer"] == session["correct_answer"]):
        session["score"] += 1
    else:
        session["lives"] -= 1
    if session["lives"] <= 0:
        return False
