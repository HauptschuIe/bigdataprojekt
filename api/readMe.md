# Chefkoch API

This project was created with Flask, the extensions flask_restx and flask_cors and was documented with the open-source tool Swagger. Flask enables exposure of Python functions as APIs and allows us to not only define the API, but also brings in Swagger UI for the API. 
Swagger UI is a dependency-free collection of HTML, Javascript, and CSS assets that dynamically generate beautiful documentation and sandbox from a Swagger-compliant API. Because Swagger UI has no dependencies, we were able to host it in any server environment and on our local machine. 

The purpose of this API is to retrieve the data from the graph database (in our case Neo4j) and make it available to the graphical user interface. 
 
A more detailed description of the API can be found here: https://app.swaggerhub.com/apis/Big-data/BigData/1.0.0

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/api.png" width="400" height="300">

### Getting Started	

    docker-compose build	

    docker-compose up

### api.py

The api.py file contains the app definition and the API. 

Flask App definition
```python
flask_app = Flask(__name__)
api = Api(flask_app, version='1.0', title='Chefkoch API',
          description='A rudimentary API for transferring data between Neo4j and the GUI') 
```

### API

The API connects to the Neo4j instance using an URI. 
```python
uri = 'bolt://193.196.52.201:7687'
driver = GraphDatabase.driver(uri, auth=("neo4j", "passowrd")) 
```


### Ressource Naming

In order to ensure a best-practice for the API, we have defined a namespace that helps diferentiate between similar functions or classes. 
In this case, this namespace encompasses all the related operations under the prefix /chefkoch together.
```python 
chefkoch = api.namespace('Chefkoch API', description='Basic functions for data retrieval')
```

For the definition of the endpoints we redefined the two standard responses acording to the output of each endpoint. 
For better understanding, an endpoint example looks like this: 
```python 
@chefkoch.route('/recipes-by-name/<string:name>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('name', 'Recipe name')
class Recipe(Resource):
    def get(self, name):
        with driver.session() as session:
            recipes = session.write_transaction(get_recipes_by_name, name)
            return recipes
```

This endpoint uses an input parameter in order to deliver a certain recipe by name and returns it in an array. 

### Ressource Access 
1. Recipes by name
    ```
    GET /chefkoch/recipes-by-name/<name>
    ```
2. Similar recipes based on common ingredients
    ```
    GET /similar-recipes-based-on-ingredients/<id>
    ```
3. Recipes based on user ratings
    ```
    GET /see-what-other-users-rated/<id>
    ```
4. Recipes published by the same author 
    ```
    GET /see-what-else-the-author-published/<id>
    ```
5. All recipes
    ```
    GET /all-recipes
    ```
### models.py

The models.py file uses the GraphDatabase package in order to connect to Neo4j and retrieve information. The file contains the definition of the methods that access the database using Cypher Queries. The result of each Query is being returned in an array. 

The following method delivers a recipe, its id, category, keywords and ingredients. In order to access all the properties that the query delivers, we access the different indexes of the record array. The output will then be saved in an array and returned. 

```python
def get_recipes_by_name(tx, name):
    recipes = []
    result = tx.run('match (r:Recipe) where r.name =~ $name '
                    'match (r:Recipe)-[:IS_CATEGORY_OF]-(c:Category) '
                    'return properties(r) as recipe, c.name, '
                    '[(r)-[:CONTAINS]->(i) | i.name] AS ingredients, '
                    '[(r)<-[:REFERS_TO]-(k) | k.name] AS keywords', name='.*(?i)' + name + '.*')
    for record in result:
        props = record[0]
        props['category'] = record[1]
        props['ingredients'] = record[2]
        props['keywords'] = record[3]
        recipes.append(props)
    return recipes
```
The api.py will import all the methods of the models.py file and access them by their method definition. 

## Recommendation Algorithm 

The purpose of our recommendation engine is to offer the user proper suggestions on what she or he could cook next based on their preferences. 
In order to satisfy a large number of users we have decided to make suggestions based on different criteria. Once the user chooses a certain recipe, she or he will be getting the following suggestions: 

   -	Similar Recipes based on common ingredients 
   -	Other recipes, that the author published
   -	Recipes, that users who positively rated the selected recipe, also rated
   
For the suggestions based on rating we are filtering the recipes that the users rated with at least 4 stars. This way, our user would receive proper recommendations from trusted users of Chefkoch. 

For the suggestions based on common ingredients we are selecting the top 10 recipes with the most common ingredients. In order to improve the accuracy of the results, we are also taking the tags of the recipes into consideration. 

The queries for the recommendation algorithm were tested and created in Neo4j. They were afterwards used in the different methods and ran directly from the python script. The return parameters were adjusted in order to deliver an output that can be used by the GUI. 

### Advanced Metrics
#### Advanced Metrics using only ingredients

The function get_similar_recipes_by_ingredients_advanced_metrics uses advanced metrics for recommending recipes.
The ORDER BY-Clause uses log(common_ingreds_count/all_ingreds_count)/log(min_freq) to sort recommendations.
The log-Function is used to flatten the difference between min-freq which is an integer > 0 and common_ingreds_count/all_ingreds_count which is a float between 0 and 1.
The values used by the function get smaller by using logs, but the effect on greater numbers is higher.
The value min_freq is calculated by unwinding the property totalinrecipes of every found ingredient in the ingredient which are common in both recipes.
From this list of integer, the minimum value is calculated. He represents a measure for the rareness of common ingredients.
If rare ingredients are common in recipes, these are more likely to be of interest as those being part of many recipes.
Using the min_freq is a method related to idf-Rating.
In addition, the algorithm uses the Jaccard similarity coefficient in the term common_ingreds_count/all_ingreds_count.
The number of values common in Recipe 1 AND Recipe 2 is divided by the number of values in Recipe 1 OR Recipe 2.
This is the same as intersection/union.

#### Advanced metrics taking into account keywords


In this recommending algorithm, the intersection and union of keywords in both recipes is used to refine the recommendation.
Recipes with common keywords are considered to be more relevant than those who lack common keywords.
For this reason, the logarithm of Jaccard similarity coefficient of keywords is used in the term.
