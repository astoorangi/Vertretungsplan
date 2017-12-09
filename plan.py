from urllib.request import urlopen  # Für Download
from bs4 import BeautifulSoup       # Zum Parsen
import time                         # Zum Finden des Jahres einer Vertretung
import json                         # Zum konvertieren in Json

class updateWeek():
    def __init__(self,url,datei,file='data.json'):    # 1 Instanz == Eine Url
        self.url = url
        self.datei = datei
        self.file = file

    def createUrl(self,week):                       # Erstellt URL aus self.url, self.datei und angegebener Woche
        fullUrl = self.url + str(week) + self.datei
        return(fullUrl)

    def downloadWeek(self,week):                    # Downloadet eine Woche
        html = urlopen(self.createUrl(week)).read().decode('latin2')
        return(html)

    def findNone(self,content):
        if content == "---" or content == "&nbsp;" or content == "\xa0":    # Zeichen, die "Kein Inhalt" bedeuten
            return(None)                                        # Durch None ersetzen
        else:
            return(content)                                         # Wenn Inhalt = gebe wieder Inhalt zurück

    def createTime(self,date,title): # Jeder 31.7. liegt in Sommerferien --> < 2. Halb | > 1. Halb
        daymonth = time.strptime(date,'%d.%m.')             # Fasse Tag & Monat in daymonth zusammen
        month = int(time.strftime('%m',daymonth))
        currentyear = int(time.strftime('%y'))               # currentyear = Aktuelles Jahr

        for year in range(currentyear-2,currentyear+1):
            if title.count(str(year) + '/' + str(year+1)) > 0 or title.count(str(year) + '/20' + str(year+1)) > 0:
                if month <= 7:
                    return(date + '20' + str(year + 1))
                elif month > 7:
                    return(date + '20' + str(year))

    def parseHtml(self,html):                       # Parsen des Downloads
        with open(self.file) as file: # Importiere data.json
            data = json.load(file)      # Als data

        soup = BeautifulSoup(html,"html.parser")
        title = soup.title.string
        tablesraw = soup.findAll('table')
        
        motd = None
        date = None
        for table in tablesraw:                 # Jede Tabelle
            if table.get('class') != ['subst']: # Wenn Tabelle keine Vertretungen beinhaltet => motd
                motd = table.get_text()          # Schreibe Inhalt der Tabelle in motd
                motd
                motd = motd.replace('\nNachrichten zum Tag\n','')
                motdsplit = []
                for m in motd:
                    motdsplit.append(m)
                motdsplit.pop()
                motd = ""
                for m in motdsplit:
                    motd += m
                continue                            # Aktuelle Tabelle zu Ende bearbeitet --> Abbruch der Verarbeitung
            rowsraw = table.findAll('tr')       # rowsraw = Liste mit Tabellen-Reihen
            if len(rowsraw) == 1:               # Wenn Anzahl Reihen = 1, weil keine Vertretungen verfügbar
                continue                            # Abbruch, damit keine unnötigen Informationen in json
            vertretungen=[]                     # Erstelle Liste für die Vertretungen einer Tabellen
            for row in rowsraw:                 # Jede Reihe in der Tabelle
                colsraw = row.findAll('td')         # colsraw = Liste mit allen Zellen in der Reihe
                if len(colsraw)==0:                 # Wenn Anzahl der Zelle == 0: Abbruch, damit keine leeren Reihen eingetragen werden ('th's)
                    continue
                c = 0                           # c = 0, wird durchgezählt um Inhalt Zelle herauszufinden, wird für neue Reihe hiermit resettet
                vertretung = {}                 # dict für einzelene Vertretung
                for col in colsraw:             # Jede Zelle
                    if c == 0:                          # Stunde
                        stunden = col.string
                        stunden = stunden.replace("- ","")
                        stunden = stunden.split()
                        vertretung["stunden"] = stunden
                    elif c == 1:                        # Datum
                        if self.findNone(col.string) == col.string:
                            date = col.string
                    elif c == 2:
                        vertretung["vertreter"] = self.findNone(col.string)
                    elif c == 3:                        # Klasse(n)
                        klasse = col.string
                        klasse = klasse.replace(",","")
                        klasse = klasse.split()
                        vertretung["klasse"] = klasse
                    elif c == 4:                        # Art der Vertretung(Raumvertretung, Entfall, Vertretung)
                        vertretung["art"] = self.findNone(col.string)
                    elif c == 5:                        # Altes Fach
                        vertretung["fachalt"] = self.findNone(col.string)
                    elif c == 6:                        # Neues Fach
                        vertretung["fach"] = self.findNone(col.string)
                    elif c == 7:                        # Dauerhaft leere Spalte -> wird übersprungen
                        None
                    elif c == 8:                        # Text zur Vertretung
                        vertretung["text"] = self.findNone(col.string)
                    elif c == 9:                        # Raum der Vertretung
                        vertretung["raum"] = self.findNone(col.string)
                    else:                               # Sollte c > Anzahl der Spalten werden: Warnung
                        print("Fehler: c > 9")
                    c += 1                              # c+=1, damit nächste Spalte/Zelle

                if vertretung["art"] == None:
                    #print(vertretungen[-1])
                    vertretungen[-1]["text"] += " " + vertretung["text"]
                    continue

                vertretungen.append(vertretung)     # Nach allen Zellen: Füge Vertretung in Liste Vertretungen zusammen
                olddate = date                      # Altes Datum = Datum, für nächste Runde
            daycontent = {"motd":motd,"vertretungen":vertretungen}  # Füge Motd und Liste der Vertretungen des Tages in daycontent zusammen
            motd = None                             # Leere motd, damit gleich nicht mehr vorhanden
            date = self.createTime(date,title)      # Füge mit Funktion date Jahr zum Datum hinzu
            data["days"][date] = {}                 # Leere bisherigen dict zum Datum
            data["days"][date] = daycontent         # Fülle dict des Datums mit daycontent

        with open(self.file,'w') as file:         # Öffne data.json
            file.write(json.dumps(data,indent=None))   # Speichere in data.json ab, indent = Einrückung (None = Alles eine Zeile)
                    

    def update(self,week):                          # Starten eines Updates einer Woche
        html = self.downloadWeek(week)
        self.parseHtml(html)


class get():
    def __init__(self,file="data.json"):
        self.file = file
    
    def search(self,date,isklasse):     # Suche nach Vertretungen
        with open(self.file) as file:   # Importiere data.json
            data = json.load(file)      # Als data
        sortedVertretungen = []
        for vertretung in data["days"][date]["vertretungen"]:   # Jede Vertretung
            for klasse in vertretung["klasse"]:         # Jede Klasse
                counter = klasse.count(str(isklasse))       # Zähle Anzahl der gesuchten Klasse pro Klasse
                if counter > 0:                             # Wenn Suchbegriff gefunden
                    sortedVertretungen.append(vertretung)       # Füge Vertretung hinzu
                    break                                       # Breche aktuelle Vertretung ab, da bereits hinzugefügt
        return({date:sorted(sortedVertretungen, key=lambda vertretung: vertretung["stunden"][0])})

    def motd(self,date):
        with open(self.file) as file:   # Importiere data.json
            data = json.load(file)      # Als data
        return(data["days"][date]["motd"])
