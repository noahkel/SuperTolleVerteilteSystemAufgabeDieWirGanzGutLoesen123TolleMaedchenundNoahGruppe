import logging
from flask import Flask,jsonify, Markup
from flask import request, render_template
import json 
import time


app = Flask(__name__)

logger = logging.getLogger('werkzeug') # grabs underlying WSGI logger
handler = logging.FileHandler('logfile.log') # creates handler for the log file
logger.addHandler(handler)

blackboards = {}


@app.route('/')
def hello_world():
    return render_template('index.html')

#localhost:5000/createBlackboard?name=AlexandrasBlackboard&gueltigkeit=5000
@app.route('/createBlackboard')
def create_blackboard():
    name = request.args.get('name')
    if len(name) > 32:
        return render_template('template.html', variable= "Name darf maximal 32 Zeichen besitzen." )
       
    gueltigkeit = request.args.get('gueltigkeit', type=float)
    if gueltigkeit == None:
        return render_template('template.html', variable= "Gültigkeit muss ne nummer sein du schlingel." )

    if name in blackboards:
        return render_template('template.html', variable= "Dieses Blackboard gibt es schon du schlingel." )
    if gueltigkeit == 0:
        ablaufzeit = time.time()
    else:
        zeitstempel = time.time()
        ablaufzeit = zeitstempel + gueltigkeit

    blackboards[name] = {"Daten" : "" , 
    "Gueltigkeit" : ablaufzeit,
    "DeltaZeit": gueltigkeit
    }
    return render_template('template.html', variable="Blackboard " + name + " wurde erstellt." )

#localhost:5000/displayBlackboard?name=AlexandrasBlackboard&daten=hallo zusammen parti bei mir
#displayBlackboard
@app.route('/displayBlackboard')
def display_blackboard():
    name = request.args.get('name')
    daten = request.args.get('daten')#check ob es die parameter gibt
    if len(daten) > 420:
        return render_template('template.html', variable="Daten darf maximal 420 Zeichen besitzen du Schlingel." )
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
        return render_template('template.html', variable="Blackboard " + name + " wurde erfolgreich aktualisiert." )
    else:
        return render_template('template.html', variable="Blackboard existiert nicht du Schlingel.")
    
#localhost:5000/clearBlackboard?name=AlexandrasBlackboard
#clearBlackboard
@app.route('/clearBlackboard')
def clear_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        blackboards[name]["Daten"]  = ""
        blackboards[name]["Gueltigkeit"]= time.time()
        return render_template('template.html', variable="Blackboard " + name + " wurde erfolgreich aktualisiert." )
    else:
        return render_template('template.html', variable="Blackboard existiert nicht du Schlingel.")

#localhost:5000/readBlackboard?name=AlexandrasBlackboard
#readBlackboard
@app.route('/readBlackboard')
def read_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        if time.time()<blackboards[name]["Gueltigkeit"] or blackboards[name]["DeltaZeit"] == 0  :
            gueltigkeit = "Gültig"
            farbe = "green"
        else:
            gueltigkeit = "Ungültig"
            farbe = "red"
        return render_template('template.html', farbe=farbe, variable =gueltigkeit,variable2= str(blackboards[name]["Daten"]) )
    else:
        return render_template('template.html', variable="Blackboard existiert nicht du Schlingel.")

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
            farbe = "green"
        else:
            gueltigkeit = "Ungültig"
            farbe = "red"
        return render_template('template.html',farbe = farbe,variable =gueltigkeit,variable2= volloderleer, variable3 = "Aktualisiert am: "+ aktualisierung  )
   
    else:
        return render_template('template.html', variable="Blackboard existiert nicht du Schlingel.")

#localhost:5000/listBlackboards
#list
@app.route('/listBlackboards')
def list_blackboards():
    if len(blackboards.keys()) == 0:
        return render_template('template.html', variable="Kein Blackboard existiert.")
    else:
        namen = ""
        for name in blackboards.keys():
            namen += name + '<br>'
        namen =  Markup(namen)
        return render_template('template.html', variable="Die vorhandenen Blackboards sind: ", variable2 = namen)

#localhost:5000/deleteBlackboard?name=AlexandrasBlackboard
#delete
@app.route('/deleteBlackboard')
def delete_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        del blackboards[name]
        return render_template('template.html', variable="Blackboard " + name + " wurde erfolgreich gelöscht." )
    else:
        return render_template('template.html', variable="Was es nicht gibt, kann man nicht löschen :).")

#localhost:5000/deleteAllBlackboards
#deleteAllBlackboards
@app.route('/deleteAllBlackboards')
def delete_all_blackboard():
    blackboards.clear()
    return render_template('template.html', variable="Alle Blackboards wurden gelöscht.")