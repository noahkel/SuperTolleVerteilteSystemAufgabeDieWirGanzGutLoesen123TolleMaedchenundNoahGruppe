import logging
from flask import Flask,jsonify, Markup
from flask import request, render_template
import json 
import time


app = Flask(__name__)

logger = logging.getLogger('werkzeug') # holt sich logger
handler = logging.FileHandler('logfile.log') # erstellt handler für log file
logger.addHandler(handler)

#JSON-String zum Speichern der Blackboards
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
    name = request.args.get('name')                             # parameter aus URL wird abgerufen
    if len(name) > 32:                                          # überprüft parameter name auf Länge und gibt ggf Fehler zurück 
        return render_template('template.html', variable= "Name darf maximal 32 Zeichen besitzen." )
       
    gueltigkeit = request.args.get('gueltigkeit', type=float)
    if gueltigkeit == None:                                     # überprüft Gültigkeit auf Richtigkeit und gibt ggf Fehler zurück 
        return render_template('template.html', variable= "Gültigkeit muss in Sekunden angegeben werden. Zeiten sind Zahlen." )

    if name in blackboards:                                     # Überprüft ob Blackboard bereits existiert
        return render_template('template.html', variable= "Dieses Blackboard existiert schon. Versuchen Sie es mit einem andren Namen." )
    if gueltigkeit == 0:                                        # Wenn Gültigkeitsparameter gleich Null, gibt es keine Ablaufzeit --> DeltaZeit=0 in JSON 
        ablaufzeit = time.time()
    else:
        zeitstempel = time.time()
        ablaufzeit = zeitstempel + gueltigkeit

    #speichert Daten in JSON Variable "blackboards"
    blackboards[name] = {"Daten" : "" , 
    "Gueltigkeit" : ablaufzeit,                                 # Zeitpunkt des Ablaufens, also aktuelle Zeit + Gültigkeitswert
    "DeltaZeit": gueltigkeit                                    # Gültigkeitswert wird auch gespeichert,damit er beim Bearbeiten des Blackboards zur Verfügung steht
    }
    #gibt gerendertes html template zurück
    return render_template('template.html', variable="Blackboard " + name + " wurde erstellt." )

#localhost:5000/displayBlackboard?name=Name_des_Blackboards&daten=Daten_des_Blackboards
#Aktualisiert den Inhalt und Zeitstempel des Blackboard
#name: Name des Blackboards, daten: neue Information
@app.route('/displayBlackboard')
def display_blackboard():
    name = request.args.get('name')
    daten = request.args.get('daten')
    if len(daten) > 420:                                        # überprüft parameter daten auf Länge und gibt ggf Fehler zurück 
        return render_template('template.html', variable="Daten darf maximal 420 Zeichen. Versuchen Sie es mit einer kürzeren Nachricht." )
    if name in blackboards:                                     #prüft ob das Blackboard existiert
        deltazeit = float(blackboards[name]["DeltaZeit"])
        #überschreibt neue Zeitinformationen
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
        blackboards[name]["Daten"]  = ""                        #überschreibt den Inhalt des Blackboards mit ""
        blackboards[name]["Gueltigkeit"]= time.time()           #Zeit des Ablaufens wird auf aktuelle Zeit gesetzt --> Blackboard nicht mehr gültig
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
    #Inhalt und Gültigkeit des Blackboards werden zurückgegeben
    if name in blackboards:
        if time.time()<blackboards[name]["Gueltigkeit"] or blackboards[name]["DeltaZeit"] == 0  :
            gueltigkeit = "Gültig"
            farbe = "green"
        else:
            gueltigkeit = "Ungültig"
            farbe = "red"

        #das Template wird mit verschiedenen Variablen gerendert
        return render_template('template.html', farbe=farbe, variable =gueltigkeit,variable2= str(blackboards[name]["Daten"]) )
    else:
        return render_template('template.html', variable="Blackboard existiert nicht.")

#localhost:5000/getBlackboardStatus?name=Name_des_Blackboards
#Gibt den aktuellen Status eines Blackboards zurück
#name: Name des Blackboards
@app.route('/getBlackboardStatus')
def get_blackboard_status():
    name = request.args.get('name')
    #Überprüft Daten des Blackboards und gibt diese je nach Informationen zurück
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
        #eine Liste mit Namen der Blackboards werden als html Liste in das Template eingebunden
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
    blackboards.clear()                             #Löscht den gesamten Inhalt des JSON-Strings in dem die Blackboard gespeichert sind
    return render_template('template.html', variable="Alle Blackboards wurden gelöscht.")