import os
import datetime, time
from flask import Flask, request
from utils import db
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route("/")
def home():
  return """<center><h1>Home page of python bot</h1><center><p>Available urls: /api</p>"""

@app.route("/api")
def api():
  return """<center><h1>Available endpoints:</h1><center><p>/api/ping<br>/api/balance (userid=discord_id optional)<br>/api/bank (userid=discord_id optional) (IN_DEV)<br>/api/inventory (userid=discord_id optional)</p>"""

@app.route("/api/ping")
def ping():
  try:
    return {"ping": db["ping"]}
  except Exception as e:
    return {"ping": -1}

@app.route("/api/balance")
def balance():
  query_parameters = request.args
  userid = query_parameters.get("userid")
  if userid:
    return {"balance": db["balance"][str(userid)]}
  else:
    return db["balance"]

@app.route("/api/bank")
def bank():
  query_parameters = request.args
  userid = query_parameters.get("userid")
  if userid:
    return {"bank": db["bank"][str(userid)]} if str(userid) in db["bank"] else ({"message": "The user could not be found.", "status": 404}, 404)
  else:
    return db["bank"]

@app.route("/api/inventory")
def inventory():
  query_parameters = request.args
  userid = query_parameters.get("userid")
  if userid:
    return db["inventory"][str(userid)] if str(userid) in db["inventory"] else ({"message": "The user could not be found.", "status": 404}, 404)
  else:
    return db["inventory"]