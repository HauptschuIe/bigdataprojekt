from neo4j import GraphDatabase


# db connection
def __init__(self, uri, user, password):
    self.driver = GraphDatabase.driver(uri, auth=('neo4j', 'larisa16'))


def close(self):
    self.driver.close()


# method returns recipes by name
# the name parameter is case sensitive and can deliver more recipes that contain the parameter value
def get_recipes_by_name(tx, name):
    recipes = []
    result = tx.run(
                    'match (r:Recipe)-[:IS_CATEGORY_OF]-(c:Category)  where r.name =~ $name '
                    'unwind[(r) - [:CONTAINS]->(i) | i.name] as ings '
                    'return properties(r) as recipe, c.name, '
                    'collect(distinct ings) AS ingredients, '
                    '[(r)<-[:REFERS_TO]-(k) | k.name] AS keywords', name='.*(?i)' + name + '.*')
    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        recipes.append(props)
    return recipes


# returns similar recipes based ONLY on common ingredients and orders them based on the number of the common ingredients
def get_similar_recipes_to(tx, rec_id):
    similar_recipes = []
    result = tx.run('match (r:Recipe)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(rec:Recipe) '
                    'where r.id =$id with rec, count(i) as commonIngredients '
                    'match (rec:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(rec) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as ingreds, rec, c, commonIngredients '
                    'return properties(rec) as recipe, c.name, '
                    'ingreds, [(rec)<-[:REFERS_TO]-(k) | k.name] AS keywords order BY commonIngredients desc limit 10',
                     id=rec_id)

    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        similar_recipes.append(props)
    return similar_recipes


# returns all the recipes in the database; created for test purposes
def get_all_recipes(tx):
    recipes = []
    result = tx.run('match (i:Ingredient)<-[:CONTAINS]-(rec:Recipe) '
                    'match (rec:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(rec) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as ingreds, rec, c '
                    'return properties(rec) as recipe, c.name, '
                    'ingreds, [(rec)<-[:REFERS_TO]-(k) | k.name] AS keywords order BY rec.name')
    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        recipes.append(props)
    return recipes


# returns recipes based on user rating; user rating >= 5
def see_what_other_users_rated(tx, rec_id):
    recipes_by_rating = []
    result = tx.run('match (r:Recipe)<-[rat:RATES]-(u:User)-[:RATES]->(rec:Recipe) '
                    'where rec.id=~$id and toInteger(rat.rating)>=5 and toInteger(rat.rating) >= 5 '
                    'with r, count(*) as commonRatings '
                    'match (r:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(r) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as ingreds, r, c, commonRatings '
                    'return properties(r) as props, c.name, '
                    'ingreds, [(r)<-[:REFERS_TO]-(k) | k.name] AS keywords, commonRatings '
                    'order by commonRatings desc limit 10',
                    id=rec_id)
    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        recipes_by_rating.append(props)
    return recipes_by_rating


# returns recipes published by the same author
def see_what_else_the_author_published(tx, rec_id):
    recipes_by_author = []
    result = tx.run('match (rec:Recipe)<-[:PROVIDES]-(u:User)-[:PROVIDES]->(r:Recipe) '
                    'where rec.id=~$id '
                    'match (r:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(r) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as ingreds, r, c '
                    'return properties(r) as props, c.name, '
                    'ingreds, [(r)<-[:REFERS_TO]-(k) | k.name] AS keywords', id=rec_id)
    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        recipes_by_author.append(props)
    return recipes_by_author


# returns similar recipes based on ingredients and calculates their frequency in both recipes for more accuracy
# for further explanations see readME.md
def get_similar_recipes_by_ingredients_advanced_metrics(tx, rec_id):
    similar_recipes = []
    result = tx.run('match (r:Recipe)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(rec:Recipe) '
                    'where r.id =$id with rec, r '
                    'match (rec:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(rec) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as ingreds, rec, r, c '
                    'unwind[(r) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as original_ingreds, '
                    'ingreds, rec, r, c '
                    'unwind[(rec) - [:CONTAINS]->(i)<-[:CONTAINS]-(r:Recipe) | i.name] as common_ings '
                    'with collect(distinct common_ings) as common_ingreds, '
                    'count (distinct common_ings) as common_ingreds_count, '
                    'ingreds, original_ingreds, rec, r, c '
                    'unwind[(rec) - [:CONTAINS]->(i)<-[:CONTAINS]-(r:Recipe) | i.totalinrecipes] as ing_freq '
                    'with avg(ing_freq) as avg_freq, min(ing_freq) as min_freq, '
                    'common_ingreds, common_ingreds_count, ingreds, original_ingreds, rec, c '
                    'unwind(ingreds + original_ingreds) as all_ings '
                    'with count(distinct all_ings) as all_ingreds_count , '
                    'collect(distinct all_ings) as all_ingreds, avg_freq, min_freq, '
                    'common_ingreds, common_ingreds_count, ingreds, original_ingreds, rec, c '
                    'return properties(rec) as recipe, c.name, ingreds, '
                    '[(rec)<-[:REFERS_TO]-(k) | k.name] AS keywords '
                    'order BY log(common_ingreds_count/all_ingreds_count)/log(min_freq) desc limit 10',
                     id=rec_id)

    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        similar_recipes.append(props)
    return similar_recipes


# returns similar recipes based on ingredients and keywords
# calculates ingredients frequency in both recipes for more accuracy
# for further explanations see readME.md
def get_similar_recipes_by_ingredients_and_keywords(tx, rec_id):
    similar_recipes = []
    result = tx.run('match(r: Recipe)-[: CONTAINS]->(i:Ingredient) < -[: CONTAINS]-(rec:Recipe) where '
                    'r.id =$id with rec, r match(rec: Recipe)-[: IS_CATEGORY_OF]-(c:Category) '
                    'unwind[(rec) - [:CONTAINS]->(i) | i.name] as ings with collect(distinct ings) as ingreds, '
                    'rec, r, c unwind[(r) - [:CONTAINS]->(i) | i.name] as ings '
                    'with collect(distinct ings) as original_ingreds, ingreds, rec, r, c '
                    'unwind[(rec) - [:CONTAINS]->(i) < -[: CONTAINS]-(r:Recipe) | i.name] as common_ings '
                    'with collect(distinct common_ings) as common_ingreds, count(distinct common_ings) '
                    'as common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'unwind[(rec) - [:CONTAINS]->(i) < -[: CONTAINS]-(r:Recipe) | i.totalinrecipes] '
                    'as ing_freq with avg(distinct ing_freq) as avg_freq, min(ing_freq) as min_freq, '
                    'common_ingreds, common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'unwind(ingreds + original_ingreds) as all_ings '
                    'with count(distinct all_ings) as all_ingreds_count, '
                    'collect(distinct all_ings) as all_ingreds, '
                    'avg_freq, min_freq, common_ingreds, '
                    'common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'unwind[(rec) < - [:REFERS_TO] - (k) | k.name] as keywords '
                    'with collect(distinct keywords) as keywds, '
                    'all_ingreds_count, all_ingreds, avg_freq, min_freq, '
                    'common_ingreds, common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'unwind[(r) < - [:REFERS_TO] - (k) | k.name] as keywords '
                    'with collect(distinct keywords) as original_keywds, keywds, '
                    'all_ingreds_count, all_ingreds, avg_freq, min_freq, common_ingreds, '
                    'common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'unwind[(rec) < - [:REFERS_TO] - (k) - [: REFERS_TO]->(r) | k.name] as common_keywords '
                    'with collect(distinct common_keywords) as common_keywds, '
                    'count(distinct common_keywords) as common_keywds_count, '
                    'original_keywds, keywds, all_ingreds_count, all_ingreds, '
                    'avg_freq, min_freq, common_ingreds, common_ingreds_count, '
                    'ingreds, original_ingreds, rec, r, c unwind(keywds + original_keywds) as all_keywords '
                    'with count(distinct all_keywords) as all_keywds_count, '
                    'collect(distinct all_keywords) as all_keywds, '
                    'common_keywds, common_keywds_count, original_keywds, '
                    'keywds, all_ingreds_count, all_ingreds, avg_freq, min_freq, '
                    'common_ingreds, common_ingreds_count, ingreds, original_ingreds, rec, r, c '
                    'return properties(rec) as recipe, c.name, ingreds, keywds '
                    'order BY log(common_ingreds_count / all_ingreds_count) / log(min_freq) '
                    '* log(common_keywds_count / all_keywds_count) desc limit 10', id=rec_id)

    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        if props not in similar_recipes:
            similar_recipes.append(props)
    return similar_recipes
