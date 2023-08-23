import os
import datetime, time
from flask import Flask, request, render_template
from utils import db
import hashlib
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
  return render_template("home.html")

@app.route("/api")
def api():
  return render_template("api.html")

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

@app.route("/api/testkeys")
def test():
  query_parameters = request.args
  apikey = query_parameters.get("apikey")
  if not apikey:
    return {"error": "Missing API key"}, 400
  hashed_apikey = hashlib.sha256(apikey.encode()).hexdigest()
  if hashed_apikey not in db["apikeys"]:
    return {"error": "Invalid API key"}, 404
  if not db["apikeys"][hashed_apikey]["isvalid"]:
    return {"error": "API key is invalid"}, 401
  return {"message": db["apikeys"][hashed_apikey]}
