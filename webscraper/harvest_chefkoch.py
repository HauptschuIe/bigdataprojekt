import urllib.request
from bs4 import BeautifulSoup
import json
import os
import sys
import re
import pymongo
import ray


'''Um ein vorzeitiges Stoppen zu verhindern und das Debugging zu erleichtern, 
wurde ein Exception-Handling eingeführt. Die exemplarische Erläuterung findet sich in Zeile 256 ff.'''


# der Decorator ist notwendig, dass die Klasse remote, also in einem Unterprozess, initialisiert werden kann
@ray.remote
# Klasse für die spätere Verwendung als RAY-Actor zum Sammeln der Ratings
class RatingHarvester(object):
    # Initialisierung der Klasse mit dem Parameter url_list, der Anzahl der erstellten Ratings,
    # einem Dictionary für die gesammelten Ratings und einem Dictionary für die URLs,
    # bei denen das Harvesting scheitert, für die spätere Verwendung
    def __init__(self, url_list):
        self.rating_urls = url_list
        self.ratings_nr = 0
        self.ratings = {}
        self.remaining_urls = {}

    # Funktion zum Scrapen der Ratings
    def get_ratings(self):
        for rating_url in self.rating_urls:
            # Speichern der Rating-ID in einer Variable für die Zuordnung der Ratings zum Rezept
            rating_id = re.findall(r'https://www.chefkoch.de/rezepte/wertungen/(\d+)/.*', rating_url)[0]
            try:
                # Generierung eines Beautiful-Soup-Objektes für die Verarbeitung des HTML
                rating_soup = get_beautiful_soup(rating_url)
                # Scrapen der einzelnen Rating-Tags aus der Seite
                tags_list = [tr_tag for tr_tag in rating_soup.find("table", class_="voting-table").find_all('tr')
                             if tr_tag.find_all('td')]
                self.get_ratings_from_tags_list(tags_list, rating_id)
                self.ratings_nr += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print()
                print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                    c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
                print(rating_url)
                self.remaining_urls[rating_id] = rating_url

    # Verarbeitung der einzelnen Rating-Tags und Befüllen des Dictionary
    def get_ratings_from_tags_list(self, tags_list, rating_id):
        ratings = []
        for rating in tags_list:
            # Scrapen der Sternebewertung aus dem Rating-Tag
            rating_stars = [re.findall(r'\d', rating)[0] for rating in
                            rating.find('span', class_='rating-small').find('span')['class'] if
                            re.findall(r'\d', rating)][0]
            # Prüfen, ob der User, der bewertet hat, noch angemeldet ist,
            # sonst ist die Bewertung immer 0 Sterne und verzerrt das Ergebnis,
            # zudem können die Daten dann in der Neo4J später nicht verlinkt werden
            if rating.find('a'):
                # Scrapen der User-URL
                user_url = 'https://www.chefkoch.de' + rating.find('a')['href']
                # Scrapen des Rating-Datums
                rating_date = rating.find('td', class_='votes-date-cell').text.strip()
                # Scrapen des Ratings, dass den User betrifft
                # (hier wird die Anzahl der eigenen Rezepte und Blogbeiträge berücksichtigt)
                user_rating = [re.findall(r'\d+', str(link_tag['class']))[0]
                               for link_tag in rating.find_all('a') if
                               link_tag['href'] == "http://www.chefkoch.de/benutzer/hitliste"][0]
                # Verarbeitung der Informationen zu einem Dictionary und Speicherung in einer Liste
                ratings.append(
                    {'user_url': user_url, 'rating': rating_stars, 'date': rating_date,
                     'user_rating': user_rating})
                # Anhängen der Liste an das Dictionary mit den Ratings
                self.ratings[rating_id] = ratings

    # Funktion zur Rückgabe der generierten Records und der URLs der gescheiterten Abfragen für die spätere Verwendung
    def read(self):
        return self.ratings, self.remaining_urls


@ray.remote
# Klasse für die spätere Verwendung als RAY-Actor zum Sammeln der Records
class RecordHarvester(object):
    # Initialisierung der Klasse mit dem Parameter url_list, der Anzahl der erstellten Records
    # und einem Dictionary für die gesammelten Records
    def __init__(self, url_list: list):
        self.urls = url_list
        self.records_nr = 0
        self.records = {}

    # Funktion zum Sammeln der Records
    def get_records(self):
        for recipe_url in self.urls:
            # Speichern der Rezept-ID in einer Variable für die Zuordnung der Ratings zum Rezept
            recipe_id = re.findall(r'https://www.chefkoch.de/rezepte/(\d+)/.*', recipe_url)[0]
            try:
                # Generierung eines Beautiful-Soup-Objektes für die Verarbeitung des HTML
                recipe_soup = get_beautiful_soup(recipe_url)
                # Scrapen des Tags, der das Rezept enthält,
                # Extrahierung des enthaltenen JSON-kompatiblen Strings und Laden als Dictionary
                recipe_data = \
                    [json.loads(tag.string) for tag in recipe_soup.find_all('script', type="application/ld+json") if
                     'recipeInstructions' in tag.string][0]
                # Ergänzen weiterer Informationen im Dictionary, die nicht enthalten, aber später relevant sind
                recipe_data['recipe_url'] = recipe_url
                recipe_data['id'] = recipe_id
                # Ergänzen des Users, der das Rezept erstellt hat
                if recipe_soup.find('div', class_="ds-mb ds-mb-row user-box").find('a',
                                                                                   class_="ds-copy-link bi-profile"):
                    recipe_data['user_url']\
                        = recipe_soup.find('div', class_="ds-mb ds-mb-row user-box")\
                        .find('a', class_="ds-copy-link bi-profile")['href']
                else:
                    recipe_data['user_url'] = ''
                # Speicherung des erstellten Dictionary in einem Dictionary mit dem Schlüssel Recipe-ID
                self.records[recipe_id] = recipe_data
                self.records_nr += 1
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                    c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
                print(recipe_url)

    # Funktion zur Rückgabe der generierten Records und der URLs der gescheiterten Abfragen für die spätere Verwendung
    def read(self):
        return self.records


# Funktion zur Initialisierung der RAY-Actors und dem Verteilen der einzelnen Rezept- und Rating-URLs auf die Actors
def get_records_from_recipe_urls(recipe_urls, pending_urls, my_col):
    try:
        # generieren der Rating-URLs aus den Rezept-URLs
        rating_urls = [recipe_url.replace('rezepte/', 'rezepte/wertungen/') for recipe_url in recipe_urls]
        # Initialisierung von 5 Actors, die jeweils 6 der 30 übergebenen Rezept-URLs verarbeiten
        record_harvester_actors = [RecordHarvester.remote(recipe_urls[i * 6:(i + 1) * 6]) for i in range(5)]
        # Aufruf der Funktion get_records in jedem Actor-Objekt
        [c.get_records.remote() for c in record_harvester_actors]
        # Abruf der Funktion read in jedem Actor-Objekt
        recipe_records = [c.read.remote() for c in record_harvester_actors]
        # Sammeln der Ergebnisse aus allen Unterprozessen
        recipe_records = ray.get(recipe_records)
        # Entfernen der erstellten Subprozesse, die nicht mehr benötigt werden,
        # macht sonst der Garbage-Collector (RAM freimachen)
        del record_harvester_actors
        # siehe Erklärung beim Record-Harvesting
        rating_harvester_actors = [RatingHarvester.remote(rating_urls[i * 6:(i + 1) * 6]) for i in range(5)]
        [c.get_ratings.remote() for c in rating_harvester_actors]
        ratings_records = [c.read.remote() for c in rating_harvester_actors]
        ratings_records = ray.get(ratings_records)
        # Zusammenfassen aller entstandenen Dictionaries (Flatten der Liste)
        ratings = {rating_nr: rating_record[0][rating_nr] for rating_record in ratings_records for rating_nr in
                   rating_record[0]}
        # Entpacken der Dictionaries mit den URLs, bei denen die Abfrage gescheitert ist
        remaining_rating_urls = {rating_nr: rating_record[1][rating_nr] for rating_record in ratings_records
                                 for rating_nr in rating_record[1]}
        del rating_harvester_actors
        # Iterieren über die Erhaltenen Dictionaries
        for recipes_list in recipe_records:
            # Iterieren über die Einträge in den Dictionaries
            for rec_nr in recipes_list:
                rec = recipes_list[rec_nr]
                # Prüfen, ob eine Liste mit Ratings erfolgreich generiert wurde
                if rec_nr in ratings:
                    # Anreichern des Rezeptes mit den Ratings
                    rec['ratings'] = ratings[rec_nr]
                    # Dictionary in die MongoDB schreiben
                    my_col.insert_one(rec)
                # Falls die Generierung der Ratings fehlgeschlagen ist, Speichern der URLs in der Warteschlange
                else:
                    pending_urls[rec_nr] = [rec['recipe_url'], remaining_rating_urls[rec_nr]]
                    print(pending_urls)
        return pending_urls
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
            c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
        return {}

# Funktion zur Generierung eines Beautiful-Soup-Objektes auf Basis einer URL
def get_beautiful_soup(url):
    try:
        # Abruf der Seite mit einem hohen Timeout für das Laden umfangreicher Ratingseiten
        with urllib.request.urlopen(url, timeout=15) as url_response:
            # Lesen der erhaltenen Daten
            page = url_response.read()
            # Decodierung in UTF-8 zur Vermeidung der Encodierung von Sonderzeichen
            page = page.decode('utf-8')
            # Generierung eines BeautifulSoup-Objektes
            soup = BeautifulSoup(page, 'html.parser')
        return soup
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
            c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
        print(url)
        return None


# Hauptfunktion
def get_recipes():
    try:
        # Initialisierung von RAY mit 8 CPUs, da sonst oft Actors nicht initialisiert werden können und warten,
        # sodass Zeit verloren geht
        ray.init(num_cpus=8)
        # Initialisierung eines Clients für die MongoDB
        my_client = pymongo.MongoClient('193.196.55.40', 27017)
        # Richten des Cursors auf die gewünschte Datenbank
        my_db = my_client["chefkoch"]
        # Richten des Cursors auf die gewünschte Collection in der Datenbank
        my_col = my_db["recipes"]
        recipe_nr = 0
        pending_urls = {}
        while True:
            try:
                # Erneuter Versuch, die URLs zu harvesten, bei denen der Versuch nicht erfolgreich war,
                # falls eine bestimmte Anzahl zusammengekommen ist
                if len(pending_urls) >= 25:
                    pending_urls_to_harvest = [pending_urls[recipe_nr][0] for recipe_nr in pending_urls]
                    get_records_from_recipe_urls(pending_urls_to_harvest, pending_urls, my_col)
                    # Leeren der Warteschlange (nach zwei Versuchen wird das Rezept für diesen Durchlauf verworfen)
                    pending_urls = {}
                # Zusammenbauen einer Seite in der Gesamtrezepteliste
                all_recipes_url = 'https://www.chefkoch.de/rs/s' + str(recipe_nr) + '/Rezepte.html'
                print(all_recipes_url)
                # Erhöhen der Rezepteanzahl um 30 für den nächsten Durchlauf,
                # da 30 Treffer auf einer Seite angezeigt werden
                recipe_nr += 30
                all_recipes_soup = get_beautiful_soup(all_recipes_url)
                # Scrapen aller Tags, die auf Rezepte verweisen
                recipes_tags_list = [json.loads(tag.string) for tag in
                                     all_recipes_soup.find_all('script', type="application/ld+json")
                                     if 'itemListElement' in json.loads(tag.string)]
                # Falls die Rezeptnummer der aufgerufenen Seite zu hoch ist, sind dort keine Rezepte vorhanden
                # wenn das der Fall ist, soll die Gesamtmenge erneut durchlaufen werden
                if not recipes_tags_list[0]['itemListElement']:
                    recipe_nr = 0
                else:
                    # Estrahieren der URLs aus den Rezept-Tags
                    recipes_urls = [recipe['url'] for recipe in recipes_tags_list[0]['itemListElement']
                                    if not my_col.find_one({'id': re.findall(r'https://www.chefkoch.de/rezepte/(\d+)/.*',
                                                                             recipe['url'])[0]})]
                    if recipes_urls:
                        # Verwendung der generierten URLs, um diese auf die Actors zu verteilen
                        pending_urls_this_time = get_records_from_recipe_urls(recipes_urls, pending_urls, my_col)
                        # Übertragung der übrigen URLS in die Warteschlange
                        for rec_nr in pending_urls_this_time:
                            pending_urls[rec_nr] = pending_urls_this_time[rec_nr]
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                    c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
    except Exception as e:
        # Abrufen der Informationen über das Modul, in dem der Fehler aufgetreten ist und die Art des Fehlers
        exc_type, exc_obj, exc_tb = sys.exc_info()
        # Abruf des Namens des Moduls
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # Ausgabe des formatierten Error Strings mit Informationen über die Art des Fehlers
        # und die genaue Stelle im Code, an der dieser aufgetreten ist
        print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
            c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))


if __name__ == '__main__':
    get_recipes()
