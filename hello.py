from flask import Flask,jsonify
from flask import request
import json 
import time

app = Flask(__name__)

#blackboards = { "meinBlackboard": 
#    {"Daten" : "HeutePartyInTheHood" , 
#    "Gueltikgkeit" : 1565645464.15,
#    "DeltaZeit": 5
#    },
#    "NoahsBlackboard":
#    {"Daten" : "HeutePartyInTheHood" , 
#    "Gueltikgkeit" : 1565645464.15
#    },
#}
blackboards = {}

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/newtable')
def query_example():
    # if key doesn't exist, returns None
    language = request.args.get('table')

    return '''<h1>The table name is: {}</h1>'''.format(language)

#localhost:5000/createBlackboard?name=AlexandrasBlackboard&gueltigkeit=5000
@app.route('/createBlackboard')
def create_blackboard():
    name = request.args.get('name')
    if len(name) > 32:
        return '''<h1>Name darf maximal 32 Zeichen besitzen</h1>'''
       
    gueltigkeit = request.args.get('gueltigkeit', type=float)
    if gueltigkeit == None:
        return '''<h1>Gültigkeit muss ne nummer sein du schlingel</h1>'''

    if name in blackboards:
        return '''<h1>Dieses Blackboard gibt es schon du schlingel</h1>'''
    if gueltigkeit == 0:
        ablaufzeit = time.time()
    else:
        zeitstempel = time.time()
        ablaufzeit = zeitstempel + gueltigkeit

    blackboards[name] = {"Daten" : "" , 
    "Gueltigkeit" : ablaufzeit,
    "DeltaZeit": gueltigkeit
    }
    return jsonify(blackboards)

#localhost:5000/displayBlackboard?name=AlexandrasBlackboard&daten=hallo zusammen parti bei mir
#displayBlackboard
@app.route('/displayBlackboard')
def display_blackboard():
    name = request.args.get('name')
    daten = request.args.get('daten')#check ob es die parameter gibt
    if len(daten) > 420:
        return '''<h1>Daten darf maximal 420 Zeichen besitzen du schlingel</h1>'''
    if name in blackboards:
        deltazeit = float(blackboards[name]["DeltaZeit"])
        if deltazeit == 0:
            ablaufzeit = time.time()
        else:
            zeitstempel = time.time()
            ablaufzeit = zeitstempel + deltazeit
        blackboards[name] = {"Daten" : daten , 
            "Gueltigkeit" : ablaufzeit,
            "DeltaZeit": deltazeit
            }
        return jsonify(blackboards)
    else:
        return '''<h1>Blackboard existiert nicht du Schlingel</h1>'''
    
#localhost:5000/clearBlackboard?name=AlexandrasBlackboard
#clearBlackboard
@app.route('/clearBlackboard')
def clear_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        blackboards[name]["Daten"]  = ""
        blackboards[name]["Gueltigkeit"]= time.time()
        return jsonify(blackboards)
    else:
        return '''<h1>Blackboard existiert nicht du Schlingel</h1>'''

#localhost:5000/readBlackboard?name=AlexandrasBlackboard
#readBlackboard
@app.route('/readBlackboard')
def read_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        if time.time()<blackboards[name]["Gueltigkeit"] or blackboards[name]["DeltaZeit"] == 0  :
            gueltigkeit = "Gültig"
        else:
            gueltigkeit = "Ungültig"
        return '''<h1>{}</h1> <h1>{}</h1>'''.format(gueltigkeit, str(blackboards[name]["Daten"]))
    else:
        return '''<h1>Blackboard existiert nicht du Schlingel</h1>'''

#localhost:5000/getBlackboardStatus?name=AlexandrasBlackboard
#getBlackboardStatus
@app.route('/getBlackboardStatus')
def get_blackboard_status():
    name = request.args.get('name')
    if name in blackboards:
        if blackboards[name]["Daten"]  == "":
            volloderleer= "Leer"
        else:
            volloderleer= "Gefüllt"

        aktualisierungszeitpunkt = float(blackboards[name]["Gueltigkeit"])-float(blackboards[name]["DeltaZeit"])
        aktualisierung = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(aktualisierungszeitpunkt))
        
        if time.time()<blackboards[name]["Gueltigkeit"] or blackboards[name]["DeltaZeit"] == 0  :
            gueltigkeit = "Gültig"
        else:
            gueltigkeit = "Ungültig"

        return '''<h1>{}</h1> <h1>{}</h1><h1>Aktualisiert am: {}</h1>'''.format(volloderleer, gueltigkeit,aktualisierung)
   
    else:
        return '''<h1>Blackboard existiert nicht du Schlingel</h1>'''

#localhost:5000/listBlackboards
#list
@app.route('/listBlackboards')
def list_blackboards():
    if len(blackboards.keys()) == 0:
        return '''<h1>Kein Blackboard existiert du Schlingel</h1>'''
    else:
        namen = "<h1>Die Vorhandenen Blackboards sind: </h1>"
        for name in blackboards.keys():
            namen += "<h1>" + name + "</h1>"
        return '''{}'''.format(namen)

#localhost:5000/deleteBlackboard?name=AlexandrasBlackboard
#delete
@app.route('/deleteBlackboard')
def delete_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        del blackboards[name]
        return jsonify(blackboards)
    else:
        return '''<h1>Was es nicht gibt kann man nicht löschen Sie Schlingel</h1>'''

#localhost:5000/deleteAllBlackboards
#deleteAllBlackboards
@app.route('/deleteAllBlackboards')
def delete_all_blackboard():
    blackboards.clear()
    return jsonify(blackboards)