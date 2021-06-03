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

#localhost:5000/
#Anleitung aller Funktionen und Zugriff darauf.
@app.route('/')
def hello_world():
    return render_template('index.html')


#localhost:5000/createBlackboard?name=Name_des_Blackboards&gueltigkeit=Dauer_der_Gültigkeit_des_Blackboards_in_Sekunden
#Erstellung eines neuen Blackboards
#name: Name des Blackboards, gueltigkeit: Ablaufzeit in Sekunden
@app.route('/createBlackboard')
def create_blackboard():
    name = request.args.get('name')
    if len(name) > 32:
        return render_template('template.html', variable= "Name darf maximal 32 Zeichen besitzen." )
       
    gueltigkeit = request.args.get('gueltigkeit', type=float)
    if gueltigkeit == None:
        return render_template('template.html', variable= "Gültigkeit muss in Sekunden angegeben werden. Zeiten sind Zahlen." )

    if name in blackboards:
        return render_template('template.html', variable= "Dieses Blackboard existiert schon. Versuchen Sie es mit einem andren Namen." )
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

#localhost:5000/displayBlackboard?name=Name_des_Blackboards&daten=Daten_des_Blackboards
#Aktualisiert den Inhalt und Zeitstempel des Blackboard
#name: Name des Blackboards, daten: neue Information
@app.route('/displayBlackboard')
def display_blackboard():
    name = request.args.get('name')
    daten = request.args.get('daten')#check ob es die parameter gibt
    if len(daten) > 420:
        return render_template('template.html', variable="Daten darf maximal 420 Zeichen. Versuchen Sie es mit einer kürzeren Nachricht." )
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
        return render_template('template.html', variable="Blackboard existiert nicht.")
    
#localhost:5000/clearBlackboard?name=Name_des_Blackboards
#Löscht den Inhalt eines Blackboards. Blackboard ist nicht mehr Gültig
#name: Name des Blackboards
@app.route('/clearBlackboard')
def clear_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        blackboards[name]["Daten"]  = ""
        blackboards[name]["Gueltigkeit"]= time.time()
        return render_template('template.html', variable="Blackboard " + name + " wurde erfolgreich aktualisiert." )
    else:
        return render_template('template.html', variable="Blackboard existiert nicht.")

#localhost:5000/readBlackboard?name=Name_des_Blackboards
#Liest den Inhalt eines Blackboards aus. Zusätzlich wird die Gültigkeit der Daten signalisiert.
#Wenn Nachricht veraltet ist wird diese Information gegeben.
#name: Name des Blackboards
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
        return render_template('template.html', variable="Blackboard existiert nicht.")

#localhost:5000/getBlackboardStatus?name=Name_des_Blackboards
#Gibt den aktuellen Status eines Blackboards zurück
#name: Name des Blackboards
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
        return render_template('template.html', variable="Blackboard existiert nicht.")

#localhost:5000/listBlackboards
#Gibt eine Übersicht über alle vorhandenen Blackboard zurück
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

#localhost:5000/deleteBlackboard?name=Name_des_Blackboards
#Löscht ein Blackboard
#name: Name des Blackboards
@app.route('/deleteBlackboard')
def delete_blackboard():
    name = request.args.get('name')
    if name in blackboards:
        del blackboards[name]
        return render_template('template.html', variable="Blackboard " + name + " wurde erfolgreich gelöscht." )
    else:
        return render_template('template.html', variable="Was es nicht gibt, kann man nicht löschen :).")

#localhost:5000/deleteAllBlackboards
#Löscht alle vorhandenen Blackboards
@app.route('/deleteAllBlackboards')
def delete_all_blackboard():
    blackboards.clear()
    return render_template('template.html', variable="Alle Blackboards wurden gelöscht.")