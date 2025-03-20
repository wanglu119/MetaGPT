import threading

from flask import Flask, request,jsonify,send_from_directory, render_template
from flask_cors import CORS
from jsonschema import validate, ValidationError

from test import main
from metagpt.ext.werewolf.roles import Guard, Moderator, Seer, Villager, Werewolf, Witch

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

@app.route("/api/start_game",methods=["POST"])
def startGame():
  START_GAME_SCHEMA = {
     'type':'object',
     'properties': {
        'channel_name':{'type':'string'},
        'add_human':{'type':'boolean'},
        'human_player_role_name':{'type':'string',"enum":["",Guard().name, Moderator().name, Seer().name, Villager().name, Werewolf().name, Witch().name]},
        'num_werewolf':{'type':'number','minimum':1},
        'num_villager':{'type':'number','minimum':1}
     },
     'required':['channel_name','num_werewolf','num_villager']
  }
  try:
    param = request.get_json()
    if not param:
      return jsonify({"error":"No Json data received"}),400
    validate(instance=param, schema=START_GAME_SCHEMA)

    t = threading.Thread(target=main,kwargs=param)
    t.setDaemon(True)
    t.start()
    return jsonify({"status":"ok"})
  except ValidationError as e:
    return jsonify({"error": f"Validation failed: {e.message}"}), 400
  except Exception as e:
    return jsonify({"error": str(e)}), 500

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
