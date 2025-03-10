import threading

import flask
from flask import request,jsonify
from flask_cors import CORS

from test import main

app = flask.Flask(__name__)
CORS(app)

@app.route("/api/view_model_player",methods=["GET"])
def viewModelPlayer():
  channelName = request.args.get("channelName","mychannel")
  t = threading.Thread(target=main,args=[channelName])
  t.setDaemon(True)
  t.start()
  return jsonify({"status":"ok"})

@app.route("/api/human_and_model_player",methods=["GET"])
def humanAndModelPlayer():
  channelName = request.args.get("channelName","mychannel")
  t = threading.Thread(target=main,args=[channelName],kwargs={"add_human":True})
  t.setDaemon(True)
  t.start()
  return jsonify({"status":"ok"})

if __name__ == "__main__":
  app.run(host="0.0.0.0")
