# Connector between MongoDB and Neo4j

Connects MongoDB to Neo4j.

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/py2neo.png" width="400" height="300">

### Streaming from MongoDB to Neo4J

Zur Erläuterung der Parallelisierung mit RAY, der Konfiguration des MongoDB-Clients und dem Exception-Handling
sei auf das Modul harvest_chefkoch.py und die README.md im Ordner webscraper verwiesen.

#### Main function
Die Funktion beginnt mit der Erstellung und Konfiguration eines MongoClient-Objektes. 
Mit dem Client werden aus der Collection alle vorhandenen Datensätze durch Iteration abgeholt.
Über die erhaltene Liste wird so lange in 40er Schritten über die Liste iteriert, bis deren Ende erreicht ist.
In jedem Schleifendurchlauf werden remote Actors erstellt, die jeweils 10 Datensätze verarbeiten.

#### NodeCreator
Instanzen dieser Klasse werden in Subprozessen initialisiert, um vierzig Datensätze verteilt auf vier Prozesse zu bearbeiten.
Zur Erläuterung der Funktion siehe mongo2neo.py.

#### Module myneo
Dieses Modul stellt die benötigten Funktionen zur Interaktion mit der Neo4J bereit.
Jede Funktion benötigt als Parameter eine geöffnete Session Parameter, die bei der Formatierung der Query eingefügt
werden.
In den create_node-Funktionen werden Nodes mit dem übergebenen Namen und/oder der übergebenen ID erstellt, falls diese in den Parametern aufgeführt ist.
Falls der Knoten bereits existiert, bleibt er erhalten. Dies wird durch den MERGE-Befehl realisiert.
In den create_relationship-Funktionen wird zwischen Knoten mit den übergebenen Properties eine Relationship mit dem angegebenen Label hergestellt.
Dies wird ebenfalls durch den MERGE-Befehl realisiert.
Diese Funktion set_user_rating ergänzt im gefundenen User-Node eine Property rating. 
Diese Funktion ist notwendig, da bei Usern, die Rezepte bereitstellen, diese selbst aber nicht bewerten, das Rating in den Daten nicht vorhanden ist.
Falls der User aber ein Rezept bewertet, wird in den Rating-Daten die Bewertung des Users angegeben.
Die Funktion update_ingredient_count implementiert die Einführung einer Zähler-Variable für alle Ingredient-Nodes. 
Diese gibt wider, in wie vielen Rezepten die Zutat insgesamt verwendet wird.
Die Anzahl der Vorkommen wird durch das Zählen der verbundenen Nodes ermittelt, da Ingredients ausschließlich mit Rezepten verbunden sind.
Die Anzahl wird in der Property totalinrecipes abgelegt.

## Getting Started

    docker-compose build

    docker-compose up
