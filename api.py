import os
import datetime, time
from flask import Flask, jsonify, request, url_for
from flask_restful import Resource, Api
from utils import db
from dotenv import load_dotenv
load_dotenv()

def main():
  app = Flask(__name__)
  api = Api(app)

  @app.errorhandler(404)
  def page_not_found(e):
      return "<h1>404</h1><p>The resource could not be found.</p>", 404

  @app.route("/")
  def home():
    return """<center><h1>Home page</h1><center><p>Available endpoints:<br>/api/ping<br>/api/balance (userid=discord_id optional)<br>/api/bank (userid=discord_id optional) (IN_DEV)<br>/api/inventory (userid=discord_id optional)</p>"""

  class Ping(Resource):
    def get(self):
      try:
        return db["ping"]
      except Exception as e:
        return -1

  class Balance(Resource):
    def get(self):
      query_parameters = request.args
      userid = query_parameters.get("userid")
      if userid:
        return db["balance"][str(userid)] if str(userid) in db["balance"] else ({"message": "The user could not be found.", "status": 404}, 404)
      else:
        return db["balance"]

  class Bank(Resource):
    def get(self):
      query_parameters = request.args
      userid = query_parameters.get("userid")
      if userid:
        return db["bank"][str(userid)] if str(userid) in db["bank"] else ({"message": "The user could not be found.", "status": 404}, 404)
      else:
        return db["bank"]

  class Inventory(Resource):
    def get(self):
      query_parameters = request.args
      userid = query_parameters.get("userid")
      if userid:
        return db["inventory"][str(userid)] if str(userid) in db["inventory"] else ({"message": "The user could not be found.", "status": 404}, 404)
      else:
        return db["inventory"]

  api.add_resource(Ping, "/api/ping")
  api.add_resource(Balance, "/api/balance")
  api.add_resource(Bank, "/api/bank")
  api.add_resource(Inventory, "/api/inventory")
  #api.add_url_rule("/favicon.ico", redirect_to = url_for("static", filename = "favicon.ico"))

  app.run("0.0.0.0", os.environ["PORT"])

if __name__ == "__main__":
  main()