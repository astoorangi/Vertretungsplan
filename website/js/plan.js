var date = new Date();

function showInfo() {               // Zeige Klasse im Footer
    $('#infos').append(getCookie("klasse"));
}

function updateDate(anzahl) {       // Verschiebe Datum um x Tage
    date.setDate(date.getDate() + anzahl);  // Erhöhe var date um anzahl aus function
    showDate();         // Rufe functions zum aktualisieren der Ansicht auf
    showVertretungen();
}

function showDate() {               // Zeige Datum in nav        
    var wochentag = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];  // Array zum Übersetzen des Wochentages
    $('#datum').html(wochentag[date.getDay()] + ', ' + date.toLocaleDateString());  // Schreibe Wochentag und Datum in nav
}

function showVertretungen() {       // Fordere & Zeige Vertretungen in Tabelle an
    var url = "api/" + getCookie("urlhash") + "/" + date.toLocaleDateString() + "/" + getCookie("klasse");       // Erstelle URL
    $('tbody').empty();                                 // Entferne bisherige Vertretungen
    $.ajax({        // Stelle Ajax
        url: url
    })
        .done(function (data) {
            console.log(data);
            var datum = date.toLocaleDateString();          // Konvertiere Datum in tt.mm.yyyy
            var vertretungen = data[datum];     // Rufe vertretungen in Array "vertretungen"

            if (vertretungen == null) {     // Wenn Vertretunge null = Keine vorhanden
                $('tbody').append(          // Schreibe Info in Tabelle
                    '<tr>' +
                    '<td colspan="8">Keine Daten für den heutigen Tag vorhanden.</td>' +
                    '</tr>'
                );
            }

            else if (vertretungen.length == 0) {    // Wenn Anzahl der Vertretungen 0 = Keine für Auswahl vorhanden
                $('tbody').append(          // Informiere über keine Vertretungen
                    '<tr>' +
                    '<td colspan="8">Keine Vertretungen verfürbar.</td>' +
                    '</tr>'
                );
            }

            else {                                          // Else = Vertretungen für Auswahl vorhanden
                for (let vertretung of vertretungen) {              // Gehe Vertretunge in for of durch
                    var cssclass = "";                              // Definiere cssclass

                    if (vertretung.art == "Entfall") {              // Ändere nach Art der Vertretung Hintergrundfarbe der Zeilen
                        cssclass = " class=\"danger\"";             // Durch ändern der var cssclass
                    } else if (vertretung.art == "Raum-Vtr.") {
                        cssclass = " class=\"warning\"";
                    }
                    $('tbody').append(                              // Füge Vertretung hinzu
                        '<tr' + cssclass + '>' +                                                // class für Farbe nach Art
                        '<td>' + checkPrint(vertretung.stunden.toString().replace(',', ' - ')) + '</td>' +      // Stunde(n)
                        '<td>' + checkPrint(vertretung.fachalt) + '</td>' +                                     // Altes Fach
                        '<td>' + checkPrint(vertretung.fach) + '</td>' +                                        // Fach
                        '<td>' + checkPrint(vertretung.art) + '</td>' +                                         // Art
                        '<td>' + checkPrint(vertretung.raum) + '</td>' +                                        // Raum
                        '<td>' + checkPrint(vertretung.vertreter) + '</td>' +                                   // Vertreter
                        '<td>' + checkPrint(vertretung.text) + '</td>' +                                        // Text
                        '<td>' + checkPrint(vertretung.klasse.toString().replace(/,/g, ', ')) + '</td>' +        // Klasse(n)
                        '</tr>'
                    );
                };
            }

        });
}

function checkPrint(toprint) {
    if (toprint !== null) {
        return(toprint);
    }
    else {
        return("");
    }
}

function reset() {                  // Lösche Cookies & öffne Form
    var dz = new Date(0);       // var dz = 1.1.1970
    document.cookie = "klasse=; expires=" + dz + "; path=/";    // Lösche Cookie "klasse"
    document.cookie = "url=; expires=" + dz + "; path=/";       // Lösche Cookie "url"
    document.cookie = "urlhash=; expires=" + dz + "; path=/";   // Lösche Cookie "urlhash"
    checkState();               // Zum Anzeigen des Forms zum neuen Definieren der Cookies
}

function getCookie(cname) {         // Cookie nach Namen abfragen (by w3schools)
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setCookie() {              // Schreibe Cookies aus Form
    var ablauf = new Date();                // Erstelle var "ablauf" auf aktuellem Datum
    var zeit = ablauf.getTime() + (365 * 24 * 60 * 60 * 1000);  // var zeit = var ablauf + 1 Jahr
    ablauf.setTime(zeit);                   // var ablauf = var zeit

    var klasse = $('#klasse')[0].value;     // var klasse = textform "#klasse"
    var url = $('#url')[0].value;           // var url = textform "#url"
    var urlhash = sha1(url);                // var urlhash = sha1 von var url

    document.cookie = "klasse=" + klasse + "; expires=" + ablauf.toUTCString() + "; path=/";    // c klasse = var klasse
    document.cookie = "url=" + url + "; expires=" + ablauf.toUTCString() + "; path=/";          // c url = var url
    document.cookie = "urlhash=" + urlhash + "; expires=" + ablauf.toUTCString() + "; path=/";  // c urlhash = var urlhash


    checkState();                   // Blende Form aus, wenn Cookies gespeichert
}

function form(state) {              // Zeige Form an / blende aus
    if (state == true) {    // Formular anzeigen
        $('#popup').css("display", "block");        // Zeige unterschiedliche DIVs an / nicht an
        $('#content nav').css("display", "none");
        $('#content main').css("display", "none");
        $('#motd').css("display", "none");
        $.getScript("js/sha1.min.js");              // Importiere sha1 script um urlhash zu erstellen
    }
    else {                  // Formular ausblenden
        $('#popup').css("display", "none");         // Zeige unterschiedliche DIVs an / nicht an
        $('#content nav').css("display", "block");
        $('#content main').css("display", "block");
        $('#motd').css("display", "block");
        showInfo();             // Aktualisiere Daten // Doppelt????
        showDate();
        showVertretungen();
    }
}

function checkState() {             // Überprüfe, ob Cookies für Plan vorhanden oder ob Form angezeigt werden soll
    if (getCookie("klasse") == "" || getCookie("url") == "" || getCookie("urlhash") == "") {
        form(true);
    }
    else {
        form(false);
    }
}
