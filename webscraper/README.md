# Webscraper

Loads recipes from chefkoch.de and writes them into a MongoDB.

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/webscraper.png" width="400" height="300">

### Description

#### Exception-Handling
Um ein vorzeitiges Stoppen zu verhindern und das Debugging zu erleichtern, wurde ein Exception-Handling eingeführt. 
Dieses umfasst das Abrufen der Informationen über das Modul, in dem der Fehler aufgetreten ist und die Art des Fehlers.
Aus den Informationen wird der Name des Moduls extrahiert, um eine Information über die Stelle im Code zu bekommen, an der der Fehler auftritt.
Der formatierte Error String mit Informationen über die Art des Fehlers und die Stelle im Code, an der dieser aufgetreten ist, wird in der Console ausgegeben.

#### Main function
Der gesamte auszuführende Code wird in der Funktion get_recipes abgerufen, die keine Parameter entgegennimmt.
Diese Funktion wird nur aufgerufen, wenn das Modul selbst gestartet wird, nicht bei einem Import.
Zu Beginn findet eine Initialisierung von RAY mit 8 CPUs statt, da sonst oft Actors nicht initialisiert werden können und warten,
sodass Zeit verloren geht. Idealerweise werden alle Actors zeitgleich initialisiert und nehmen ihre Arbeit auf. 
Aus diesem Grund wurde auch darauf verzichtet, mehr als 5 Actors zeitgleich zu initialisieren, 
da die Systemkapazität in diesem Fall überschritten würde und es zu einem größeren Zeitverlust käme (Serielle statt parallele Verarbeitung)
Im nächsten Schritt wird ein Client für den Zugriff auf die MongoDB initialisiert. 
Der Cursor desselben soll auf die gewünschte Collection, "chefkoch" zeigen. 
Falls die Datenbank oder die Collection nicht exisiteren, werden diese automatisch erstellt.
Im nächsten Schritt wird über alle Rezept-Übersichts-Seiten auf Chefkoch iteriert, 
auf denen jeweils 30 Rezepte verfügbar sind. Die Rezept-Anzahl wird deshalb in 30er-Schritten erhöht und in die URL eingebaut.
Alle Rezept-URLs, bei denen das Harvesting scheitert, werden in einer Warteschlange gespeichert.
Bei einer Länge der Warteschlange von >= 25 wird mit diesen URLs ein erneuter Versuch gestartet.
Falls die in der URL angegebene Rezeptanzahl die Gesamtzahl der Treffer überschreitet, wird die Rezeptnummer wieder auf 0 gesetzt.
So wird ein fortlaufendes Harvesting sichergestellt.
Aus der Übersichtseite werden jeweils alle Tags gescrapt, die auf Rezepte verweisen.
#### Getting Recipes from URLs
Die generierten Rezept-URLs werden dann der Funktion get_records_from_recipe_urls zur Initialisierung der RAY-Actors und dem Verteilen der einzelnen Rezept- und Rating-URLs auf die Actors
übergeben. Diese generiert zuerst Actors in Subprozessen, die Rezeptdaten aus Rezept-URLs generieren, danach Actors, die Ratingdaten aus Rating-URLs generieren.
Die Wertungsseite ist auf Chefkoch separat von der Rezept-Seite. 
Die generierten Ergebnisse werden entpackt und zusammengeführt, sodass die Ratings in den Rezeptdaten enthalten sind.
Alle Suprozesse werden nach dem Abholen der Ergebnisse gestoppt, um den Speicherplatz freizugeben. 
Es wird über die erhaltenen Listen mit Rezept-Dictionaries iteriert und diese werden mit den Rating-Daten angereichert.
Falls das Harvesten der Ratings für eine URL fehlgeschlagen ist, wird diese in die Warteschlange hinzugefügt.
#### RecordHarvester und RatingHarvester
Zur Erläuterung der Funktion der Klassen RecordHarvester und RatingHarvester sei auf den Code mit ausführlicher Kommentierung verwiesen.

## Getting Started

    docker-compose build

    docker-compose up
