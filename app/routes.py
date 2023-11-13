import os

import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from app import app
from app.data import list_of_options
import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") 

def name_grabber(days_elapsed):
    the_days_challenge = list_of_options[days_elapsed] 
    article_title = the_days_challenge[0]
    article_subtitle = the_days_challenge[1]
    article_body = the_days_challenge[3].split('\n')

    return (article_title, article_subtitle, article_body)

def debugger():
    print("Endgame: ")
    print(session['endgame'])
    print("oneGame: ")
    print(session['oneGame'])
    print("scores: ")
    print(session['scores'])
    print("history: ")
    print(session['history'])
    print("lastday: ")
    print(session['lastday'])

def initialiser():
    # last day have you played three rounds (used to disable button)
    if 'endgame' not in session: session['endgame'] = False
    # have you played one round (used to begin printing scores)
    if 'oneGame' not in session: session['oneGame'] = False
    # scores from previous round
    if 'scores' not in session: session['scores'] = []
    # history of previous games
    if 'history' not in session: session['history'] = []
    # last day played
    if 'lastday' not in session: session['lastday'] = days_since_epoch()

def reseter():
    """
    have they played a game, but another day?
    if so, reset the session history
    """
    if session['lastday'] != days_since_epoch():
        session['endgame'] = False
        session['scores'] = []
        session['oneGame'] = False
        session['lastday'] = days_since_epoch()


def checkEndgame():
    print("Checking")
    if 'endgame' in session:
        if len(session["scores"]) >=3:
            session['endgame'] = True
    else:
        session['endgame'] = False

def endgamePrep():
    add = True
    for x in session['history']:
        if int(x[0]) == int(days_since_epoch()): add = False
    if add:
        session['history'].append([days_since_epoch(), session['todays_avg']])

def highScoreChecker():
    number_of_games = len(session['history'])
    if number_of_games > 0:
        old_scores = []
        for x in session['history']:
            old_scores.append(x[1])
        previous = max(old_scores)
    else:
        previous = "N/A"
    return (previous, number_of_games)

def addScore(score):

    if int(score) < 40: label="low"
    elif int(score) < 70: label="medium"
    else: label="high"
    session['oneGame'] = True

    if 'scores' in session:
        _scores = session["scores"]
        _scores.append([score,label])
        session["scores"] = _scores
        print(session['scores'])
    else:
        session['scores'] = [[score,label]]
        print(session['scores'])

    cumu = 0
    for s in session["scores"]:
        cumu += int(s[0])
    session['todays_avg'] = cumu / len(session['scores'])

@app.route("/", methods=("GET", "POST"))
@app.route("/index")
def index():
    initialiser()
    debugger()
    reseter()
    days_elapsed = days_since_epoch()
    beegtitle = f"Promptle #{days_elapsed}"
    prev, num = highScoreChecker()
    article_title, article_subtitle, article_body = name_grabber(days_elapsed)
    if request.method == "POST":
        question = request.form["question"]
        need_to_wait = True
        print(need_to_wait)
        question_adapted = prompt_engineering(days_elapsed, question)

        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {
                    "role": "user",
                    "content": question_adapted
                    }
                ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )  
        #response = 50 
        print("reponse: " + str(response.choices[0].message.content)) 
        need_to_wait = False
        print(need_to_wait)
        addScore(response.choices[0].message.content)
        #addScore(response)
        
        return redirect(url_for("index"))

    result = [request.args.get("result")]
    need_to_wait = False
    checkEndgame()
    if session['endgame'] == True:
        endgamePrep()
    return render_template("index.html", 
                title=article_title, subtitle=article_subtitle, body=article_body,
                 result=result, loading=need_to_wait, prev=prev, num=num, BigTitle=beegtitle)

def generate_prompt(user, true):
    prompt = f"On a scale of 0 to 100, how similar is the piece of text '{user}' to '{true}'? Your response must be in the format of a single integer."
    return prompt

def prompt_engineering(days_elapsed, question):
    true_prompt = list_of_options[days_elapsed][2]
    prompt = generate_prompt(question, true_prompt)
    return prompt


def days_since_epoch():
    today = datetime.datetime.today()
    the_epoch = datetime.datetime.strptime("11-12-2023", '%m-%d-%Y')
    gap = (today - the_epoch).days
    return gap


#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print("clearing session")
    session.clear()
    return ("nothing")