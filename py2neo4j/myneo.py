"""Dieses Modul stellt die benötigten Funktionen zur Interaktion mit der Neo4J bereit.
Jede Funktion benötigt als Parameter eine geöffnete Session Parameter, die bei der Formatierung der Query eingefügt
werden. Funktionen, die nach dem gleichen Schema funktionieren, werden blockweise erläutert"""


# Erläuterung für alle create_[node_label]_node-Funktionen
# Erstellung eines Nodes mit dem übergebenen Namen und/oder der übergebenen ID falls vorhanden.
# Falls der Knoten existiert, bleibt er erhalten.

def create_recipe_node(tx, name, recipe_id):
    tx.run("MERGE (n:Recipe { name: $name, id: $recipe_id }) RETURN n.name, n.id", name=name, recipe_id=recipe_id)


def create_category_node(tx, name):
    tx.run("MERGE (n:Category { name: $name }) RETURN n.name", name=name)


def create_ingredient_node(tx, name):
    tx.run("MERGE (b:Ingredient { name: $name }) "
           "RETURN b.name",
           name=name)


def create_keyword_node(tx, name):
    tx.run("MERGE (n:KeyWord { name: $name }) RETURN n.name", name=name)


def create_user_node(tx, name, user_id, rating=None):
    if rating:
        tx.run("MERGE (n:User { name: $name ,  id: $user_id ,  rating: $rating }) RETURN n.name",
               name=name, user_id=user_id, rating=rating)
    else:
        tx.run("MERGE (n:User { name: $name ,  id: $user_id }) RETURN n.name", name=name, user_id=user_id)


# Erläuterung für alle create_relationship-Funktionen
# Falls die Knoten mit den übergebenen Properties exisiteren,
# wird zwischen diesen eine Relationship mit dem angegebenen Label hergestellt.
# Falls die Relationship existiert, bleibt diese erhalten.

def create_relationship_ico(tx, recipe_id, category_name):
    tx.run("MATCH (a:Recipe),(b:Category) WHERE a.id = $recipe_id AND b.name = $category_name "
           "MERGE (b)-[:IS_CATEGORY_OF]->(a)",
           recipe_id=recipe_id, category_name=category_name)


def create_relationship_c(tx, recipe_id, ingredient_name, amount, amount_standard):
    tx.run("MATCH (a:Recipe),(b:Ingredient) WHERE a.id = $recipe_id AND b.name = $ingredient_name "
           "MERGE (a)-[:CONTAINS { amount: $amount , amount_standard: $amount_standard}]->(b)",
           recipe_id=recipe_id, ingredient_name=ingredient_name, amount=amount, amount_standard=amount_standard)
    # Diese Updatefunktion wird nicht verwendet, da der Knoten erst am Ende der Transaktion geschrieben wird
    # Das führt dazu, dass im Fall, dass die Zutat neu in die Datenbank kommt, der Knoten nicht gefunden werden kann.
    tx.run("MATCH (b:Ingredient) WHERE b.name = $ingredient_name "
           "SET b.totalinrecipes = b.totalinrecipes + 1",
           ingredient_name=ingredient_name)


def create_relationship_p(tx, recipe_id, user_id):
    tx.run("MATCH (a:Recipe),(b:User) WHERE a.id = $recipe_id AND b.id = $user_id MERGE (b)-[:PROVIDES]->(a)",
           recipe_id=recipe_id, user_id=user_id)


def create_relationship_rt(tx, recipe_id, keyword_name):
    tx.run(
        "MATCH (a:Recipe),(b:KeyWord) WHERE a.id = $recipe_id AND b.name = $keyword_name MERGE (b)-[:REFERS_TO]->(a)",
        recipe_id=recipe_id, keyword_name=keyword_name)


def create_relationship_r(tx, recipe_id, user_id, rating, date):
    tx.run("MATCH (a:Recipe),(b:User) WHERE a.id = $recipe_id AND b.id = $user_id "
           "MERGE (b)-[:RATES { rating: $rating, date: $date }]->(a)",
           recipe_id=recipe_id, user_id=user_id, rating=rating, date=date)


# Diese Funktion ergänzt im gefundenen User-Node eine Property rating. Diese Funktion ist notwendig, da bei Usern,
# die Rezepte bereitstellen, das Rating in den Daten nicht vorhanden ist,
# falls der selbe User aber ein Rezept bewertet, wird in den Rating-Daten die Bewertung des Users angegeben.

def set_user_rating(tx, user_id, rating):
    tx.run("MATCH (n:User { id: $user_id }) SET n += { rating: $rating } RETURN n.name, n.rating",
           user_id=user_id, rating=rating)


# Diese Funktion implementiert die Einführung einer Zähler-Variable für alle Ingredient-Nodes.
# Diese gibt wider, in wie vielen Rezepten die Zutat insgesamt verwendet wird.
# Die Anzahl der Vorkommen wird durch das Zählen der verbundenen Nodes ermittelt,
# da Ingredients ausschließlich mit Rezepten verbunden sind.
# Die Anzahl wird in der Property totalinrecipes abgelegt.

def update_ingredient_count(tx, name):
    tx.run("MATCH (n:Ingredient { name: $name})<-[r]-() "
           "WITH count(r) as relationshipnr, n "
           "SET n.totalinrecipes = relationshipnr "
           "RETURN n.name",
           name=name)
