import threading

from flask import Flask, request,jsonify,send_from_directory, render_template
from flask_cors import CORS

from test import main

app = Flask(__name__,template_folder="./frontend/dist")
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


@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")

@app.route('/<path:filename>', methods=['GET'])
def download_file(filename):
    if filename == "":
        filename="index.html"
    return send_from_directory("./frontend/dist", filename, as_attachment=True)

if __name__ == "__main__":
  app.run(host="0.0.0.0")
