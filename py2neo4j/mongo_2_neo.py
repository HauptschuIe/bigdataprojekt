from neo4j import GraphDatabase
import re
import myneo
import pymongo
import ray
import sys
import os

'''Zur Erläuterung der Parallelisierung mit RAY, der Konfiguration des MongoDB-Clients und dem Exception-Handling
sei auf das Modul harvest_chefkoch.py im Ordner webscraper verwiesen.'''


@ray.remote
# Klasse zur Generierung und Bearbeitung von Daten in der Neo4J
class NodeCreator(object):
    # Initialisierung des Objekts mit dem Neo4J-Driver und den Datensätzen aus der MongoDB
    def __init__(self, documents):
        self.docs = documents
        self.node_created_nr = 0
        # Socket-Objekte können in Remote nicht verwendet werden,
        # deshalb muss der Treiber hier in der Remote-Klasse initialisiert werden.
        self.driver = GraphDatabase.driver("bolt://193.196.54.142:7687", auth=("neo4j", "test"))

    # Funktion zum Erstellen der Nodes und Relationships in der Neo4J
    def create_nodes(self):
        try:
            for document in self.docs:
                driver = self.driver
                # Erstellen einer neuen Session mit dem initialisierten Treiber.
                # Durch die Verwendung der with-Clause wird die Session am Ende des Blocks geschlossen.
                with driver.session() as session:
                    recipe_id = document['id']
                    recipe_name = document['name']
                    # Das Erstellen der Nodes und Relationships wird im Modul myneo.py erläutert,
                    # aus dem die Funktionen importiert werden.
                    session.write_transaction(myneo.create_recipe_node, recipe_name, recipe_id)
                    session.write_transaction(myneo.create_category_node, document['recipeCategory'])
                    session.write_transaction(myneo.create_relationship_ico, recipe_id, document['recipeCategory'])
                    for ingredient in document['recipeIngredient']:
                        try:
                            # hinter dem ' , ' wird das Ingredient spezifiziert.
                            # Diese Spezifikationen wie brauner oder weißer Zucker
                            # sind für den Algorithmus zu vernachlässigen.
                            ingredient_name = ingredient.split(' , ', 1)[0]
                            print('whole Ingredient-Sting:', ingredient_name)
                            # Falls die Menge mit n. B. angegeben wird,
                            # funktionieren die unten verwendeten Regular Expressions nicht.
                            # Deshalb muss ein Sonderfall eingeführt werden.
                            # Zudem ist die Mengenangabe "nach Bedarf" zu vernachlässigen.
                            if 'n. B. ' in ingredient_name:
                                amount_standard, amount, ingredient_name = '', 'n.B.', ingredient_name.replace('n. B. ', '')
                            # falls der Zutatenstring mit einem kleinen Buchstaben beginnt, ist keine Mengenangabe vorhanden
                            # trifft z.B. auf Datensätze zu, die mit "kg" beginnen, ohne eine Mengenanbage zu machen.
                            elif ingredient[0].islower():
                                amount, ingredient_name = \
                                    re.findall(r'^([^ ]*)? ([^ ]*)?', ingredient)[0]
                                amount_standard = ''
                            # falls der Zutatenstring mit einem Leerzeichen beginnt, sind keine Mengenangaben vorhanden
                            # z.B. " Mehl , zum Bestäuben"
                            elif ord(ingredient[0]) == 32:
                                amount, amount_standard = "", ""
                                ingredient_name.strip()
                            # in allen anderen Fällen ist der String nach dem Schema
                            # "[Menge] [Maßeinheit] [Zutat]" aufgebaut, sodass dieser mit einer Regex behandelt werden kann.
                            else:
                                if re.findall('TL, [^ ]+ ', ingredient):
                                    ingredient = ingredient.replace(re.findall('TL(, [^ ]+) ', ingredient)[0], '')
                                amount, amount_standard, ingredient_name = \
                                    re.findall(r'^([^ ]*)? ([^ ]*)? (.+)', ingredient)[0]
                            # herausfiltern von unregelmäßigen Datensätzen, bei denen die Bearbeitung nicht funktioniert
                            # ca. 2 von 100 Zutaten
                            if not any(no_name for no_name in ['TL', 'EL', 'kg'] if no_name in ingredient_name):
                                ingredient_name = ingredient_name.split()[0]
                                session.write_transaction(myneo.create_ingredient_node, ingredient_name)
                                session.write_transaction(myneo.create_relationship_c, recipe_id, ingredient_name, amount,
                                                      amount_standard)
                                session.write_transaction(myneo.update_ingredient_count, ingredient_name)
                                print('Ingedient-Name: ', ingredient_name)
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                                c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
                            print(ingredient)
                    if document['user_url']:
                        # Erstellen der User-Nodes und Relationships
                        user_id = re.findall(r'profil/([^/]+)/', document['user_url'])[0]
                        user_name = re.findall(r'/([^/]+)\.html', document['user_url'])[0]
                        session.write_transaction(myneo.create_user_node, user_name, user_id)
                        session.write_transaction(myneo.create_relationship_p, recipe_id, user_id)

                    for keyword in document['keywords']:
                        # Erstellen der Keyword-Nodes und Relationships
                        session.write_transaction(myneo.create_keyword_node, keyword)
                        session.write_transaction(myneo.create_relationship_rt, recipe_id, keyword)

                    for rating in document['ratings']:
                        user_id = re.findall(r'profil/([^/]+)/', rating['user_url'])[0] \
                            if re.findall(r'profil/([^/]+)/', rating['user_url']) else None
                        if user_id:
                            # Erstellen der User-Nodes und Rating-Relationships
                            user_name = re.findall(r'/([^/]+)\.html', rating['user_url'])[0]
                            user_rating = rating['user_rating']
                            recipe_rating = rating['rating']
                            rating_date = rating['date'][0:10]
                            session.write_transaction(myneo.set_user_rating, user_id, user_rating)
                            session.write_transaction(myneo.create_user_node, user_name, user_id, user_rating)
                            session.write_transaction(myneo.create_relationship_r, recipe_id, user_id, recipe_rating,
                                                      rating_date)
                self.node_created_nr += 1
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))

    def read(self):
        return self.node_created_nr


# Hauptfunktion, die die Datensätze aus der MongoDB abruft und die Actors initialisiert
def stream_recipes_to_neo4j():
    try:
        # Erstellen und Konfigurieren eines Mongoclient-Objektes
        my_client = pymongo.MongoClient("mongodb://193.196.55.40:27017/")
        my_db = my_client["chefkoch"]
        my_col = my_db["recipes"]

        while True:
            doc_nr = 0
            # aus der Collection werden alle Datensätze durch Iteration abgeholt.
            all_docs = [doc for doc in my_col.find()]
            # Es wird so lange in 40er Schritten über die Liste iteriert, bis deren Ende erreicht ist
            while doc_nr < len(all_docs):
                try:
                    # Remote Actors werden erstellt, die jeweils 10 Datensätze verarbeiten
                    # Zum Aufruf der Funktionen siehe harvest_chefkoch.py
                    node_creator_actors = [NodeCreator.remote(all_docs[i:i + 10])
                                           for i in range(doc_nr, doc_nr + 40, 10)]
                    [nc.create_nodes.remote() for nc in node_creator_actors]
                    created_nr = [nc.read.remote() for nc in node_creator_actors]
                    created_nr = ray.get(created_nr)
                    print(sum(created_nr))
                    doc_nr += 40
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
                        c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('Error! Code: {c}, Message, {m}, Type, {t}, File, {f}, Line {line}'.format(
            c=type(e).__name__, m=str(e), t=exc_type, f=fname, line=exc_tb.tb_lineno))


if __name__ == '__main__':
    ray.init(num_cpus=8)
    stream_recipes_to_neo4j()
