import os
from flask import Flask, redirect, render_template, request, session, flash
from helpers import lookup, lookup_champs, champ_id_to_name, generate_question_skin_name, format_name, generate_question_spell_name, generate_question_mastery, compute_score
import json
from flask_session import Session
import random


#Configure application
app = Flask(__name__, static_url_path='/static')

#Configure DB using sqlite
#db = SQL("sqlite:///project.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Index to search for summoner
@app.route("/", methods=["GET", "POST"])
def index():
    filename = "https://ddragon.leagueoflegends.com/cdn/13.8.1/img/item/1104.png"
    region_codes=["LA2", "BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "NA1", "OC1"]
    region_names = ["LAS", "BR", "EUNE", "EUW", "JP", "KR", "LAN", "NA", "OCE"]
    region_info = zip(region_codes, region_names)
    return render_template("index.html", filename = filename, region_info = region_info)






@app.route("/found", methods=["GET", "POST"])
def found():
    if request.method=="POST":
        images_list = []

        # Set variables for current user in session
        session["score"] = 0
        session["user_answer"] = "1"
        session["correct_answer"] = "0"
        session["lives"] = 4

        # Store name and region entered by user
        session["summoner"]  = request.form.get("summoner")
        session["region"] = user_region = request.form.get("user_region")

        # Use it to call riot's API for encrypted summoner id (see helpers.py)
        session["summoner_id"] = lookup(session["summoner"], user_region)
        if session["summoner_id"] is None:
            flash(u"INVALID SUMMONER NAME", "error")
            return redirect("/")

        # Using summoner_id (encrypted number sent by riot's API), get most played champions by id for that user (again, peep helpers)
        session["mains_id"], session["mastery"] = lookup_champs(session["summoner_id"], user_region)
        #print(session["mastery"])

        # Convert ids to their respective champion names
        session["mains_names"] = champ_id_to_name(session["mains_id"])

        # Because of weird naming conventions used by the DB, when a champions name has a space ( ), it gets removed
        # But the second part remains uppercase. However, if it has an apostrophe ('), it gets removed and the second
        # Part becomes lowercase. format_name function handles that
        for name in session["mains_names"]:
            name = format_name(name)
            images_list.append(f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/champion/{name}.png")

        return render_template("found.html", summoner=session["summoner"], mains_names = session["mains_names"], images_list = images_list)










@app.route("/skin", methods=["GET", "POST"])
def skin():
    if request.method=="GET":
        if (compute_score() == False):
            return redirect ("/gameover")
        # Generate a question and render it on screen. Filename is the image for that question
        champion, names, id = generate_question_skin_name(session["mains_names"])
        filename = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_{id}.jpg"

        # Remember correct answer (again feels hacky / wrong)
        session["correct_answer"] = names[0]
        random.shuffle(names)
        return render_template("skin.html", summoner=session["summoner"], names = names, filename = filename, score = session["score"], lives = session["lives"])

    if request.method=="POST":
        # Remember answer from the original request
        session["user_answer"] = request.form.get("answer")

        # Chance of getting redirected to the other question type, keeps the game dynamic, will add more types
        if (random.randint(1,2) == 1):
            return redirect("/spell")
        
        if (random.randint(1,2) == 1):
            return redirect("/mastery")
        
        else:
            # If not redirected, about to generate another skin question. Compute original answer before asigning new one
            session["user_answer"] = request.form.get("answer")
        if (compute_score() == False):
            return redirect ("/gameover")
            # Generate question of the "What skin is this" type
            champion, names, id = generate_question_skin_name(session["mains_names"])
            session["correct_answer"] = names[0]
            filename = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_{id}.jpg"
            random.shuffle(names)
            return render_template("skin.html", summoner=session["summoner"],  names = names, filename = filename, score = session["score"], lives = session["lives"])









@app.route("/spell", methods=["GET", "POST"])
def spell():
    if request.method=="GET":
        if (compute_score() == False):
            return redirect ("/gameover")
        # Generate question of the "What is this spell" type
        num, names, id = generate_question_spell_name(session["mains_names"])
        filename = f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/spell/{id}.png"

        # Remember correct answer and render template
        session["correct_answer"] = names[num]
        return render_template("spell.html", summoner=session["summoner"],  names = names, filename = filename, score = session["score"], lives = session["lives"])


    if request.method=="POST":
        # If posted to spell, remember user answer in case of redirect (need it to compute score)
        session["user_answer"] = request.form.get("spell")

        # Redirect to other question types
        if (random.randint(1,2) == 1):
            return redirect("/skin")
        if (random.randint(1,2) == 1):
            return redirect("/mastery")
        
        # If posted and not redirected, compute last known answer and generate another question
        if (compute_score() == False):
            return redirect ("/gameover")
        num, names, id = generate_question_spell_name(session["mains_names"])
        filename = f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/spell/{id}.png"
        session["correct_answer"] = names[num]


    return render_template("spell.html", summoner=session["summoner"],  names = names, filename = filename, score = session["score"], lives = session["lives"])






@app.route("/mastery", methods=["GET", "POST"])
def mastery():
    if request.method == "GET":
        print(session["user_answer"])
        print(session["correct_answer"])
        if (compute_score() == False):
            return redirect ("/gameover")
        mastery, question, roll, name = generate_question_mastery(session["mains_id"], session["mastery"])
        name = format_name(name)
        filename = f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/champion/{name}.png"
        session["correct_answer"] = roll
        return render_template("mastery.html", mastery = mastery, question = question, roll = roll, filename = filename, name = name, lives = session["lives"])
    
    
    if request.method == "POST":
        if session["correct_answer"] == 1:
            if request.form.get("answer") == "LESS":
                session["score"] += 1
        if session["correct_answer"] == 2:
            if request.form.get("answer") == "MORE":
                session["score"] += 1

        if (random.randint(1,2) == 1):
            return redirect("/skin")
        if (random.randint(1,2) == 1):
            return redirect("/spell")

        mastery, question, roll, name = generate_question_mastery(session["mains_id"], session["mastery"])
        name = format_name(name)
        filename = f"https://ddragon.leagueoflegends.com/cdn/13.8.1/img/champion/{name}.png"
        session["correct_answer"] = roll

        return render_template("mastery.html", mastery = mastery, question = question, roll = roll, filename = filename, name = name, lives = session["lives"])
    



@app.route("/gameover", methods=["GET", "POST"])
def gameover():
    return render_template("gameover.html")
