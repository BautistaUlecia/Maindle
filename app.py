#Import required libraries and login_required
import os
from flask import Flask, flash, redirect, render_template, request, session
from helpers import lookup, lookup_champs, champ_id_to_name, generate_question_skin_name, format_name
import json
from flask_session import Session


#Configure application
app = Flask(__name__)

#Configure DB using sqlite
#db = SQL("sqlite:///project.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Index to search for summoner
@app.route("/", methods=["GET", "POST"])
def index():
    existing_regions=["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1"]
    return render_template("index.html", existing_regions = existing_regions)






# Summoner found page, maybe game goes here, will decide later
@app.route("/found", methods=["GET", "POST"])
def found():
    if request.method=="POST":
        mains_id = []
        images_list = []

        # Get summoner id from riot API
        session["summoner"] = summoner = request.form.get("summoner")
        session["region"] = user_region = request.form.get("user_region")
        summoner_id = lookup(summoner, user_region)
        if summoner_id is None:
            return("invalid summoner name")

        # Get mains for that summoner
        mains_id = lookup_champs(summoner_id, user_region)

        # Convert mains id to their respective champion names using riot database
        mains_names = champ_id_to_name(mains_id)

        # Create list with urls of champion images, removing spaces (the database doesnt use them)

        # Because of weird naming conventions used by the DB, when a champions name has a space ( ), it gets removed
        # But the second part remains uppercase. However, if it has an apostrophe ('), it gets removed and the second
        # Part becomes lowercase. format_name function handles that (see helpers.py)
        for name in mains_names:
            name = format_name(name)
            images_list.append(f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/champion/{name}.png")

        return render_template("found.html", summoner=summoner, mains_names = mains_names, images_list = images_list)






@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method=="POST":
        mains_id = []
        summoner = session["summoner"]
        user_region = session["region"]
        summoner_id = lookup(summoner, user_region)
        mains_id = lookup_champs(summoner_id, user_region)
        mains_names = champ_id_to_name(mains_id)
        generate_question_skin_name(mains_names)
        



        return render_template("game.html", summoner=summoner, mains_names = mains_names)






