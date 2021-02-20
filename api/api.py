from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS
from models import *
from neo4j import GraphDatabase

# define app
flask_app = Flask(__name__)
api = Api(flask_app, version='1.0', title='Chefkoch API',
          description='A rudimentary API for transferring data between Neo4j and the GUI')

# release all resources with the prefix /chefkoch for **Cross-Origin Resource Sharing** (CORS)
CORS(flask_app, resources=r'/chefkoch/*')

# db connection
uri = "neo4j://localhost:7687"
# uri = 'bolt://193.196.52.201:7687'
driver = GraphDatabase.driver(uri, auth=("neo4j", "larisa16")) # Passwort 'lala' durch eigenes Passowrt ersetzen

# namespace
chefkoch = api.namespace('Chefkoch API', description='Basic functions for Neo4j')


# endpoints
@chefkoch.route('/recipes-by-name/<string:name>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('name', 'Recipe name')
class Recipe(Resource):
    def get(self, name):
        with driver.session() as session:
            recipes = session.write_transaction(get_recipes_by_name, name)
            return recipes


@chefkoch.route('/similar-recipes-based-on-ingredients/<string:rec_id>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('rec_id', 'Recipe id')
class SimilarRecipes(Resource):
    def get(self, rec_id):
        with driver.session() as session:
            similar_recipes = session.write_transaction(get_similar_recipes_to, rec_id)
            return similar_recipes


@chefkoch.route('/see-what-other-users-rated/<string:rec_id>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('rec_id', 'Recipe id')
class RecipesByRating(Resource):
    def get(self, rec_id):
        with driver.session() as session:
            recipes_rating = session.write_transaction(see_what_other_users_rated, rec_id)
            return recipes_rating


@chefkoch.route('/see-what-else-the-author-published/<string:rec_id>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('rec_id', 'Recipe id')
class RecipesByAuthor(Resource):
    def get(self, rec_id):
        with driver.session() as session:
            recipes_author = session.write_transaction(see_what_else_the_author_published, rec_id)
            return recipes_author


@chefkoch.route('/similar-recipes-based-on-ingredients-and-keywords/<string:rec_id>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('rec_id', 'Recipe id')
class RecipesByIngredientsAndKeywords(Resource):
    def get(self, rec_id):
        with driver.session() as session:
            recipes_author = session.write_transaction(get_similar_recipes_by_ingredients_and_keywords, rec_id)
            return recipes_author


@chefkoch.route('/similar-recipes-based-on-ingredients-advanced/<string:rec_id>')
@chefkoch.response(200, 'Search results matching criteria')
@chefkoch.response(400, 'Bad input parameter')
@chefkoch.param('rec_id', 'Recipe id')
class RecipesByIngredientsAdvanced(Resource):
    def get(self, rec_id):
        with driver.session() as session:
            recipes_author = session.write_transaction(get_similar_recipes_by_ingredients_advanced_metrics, rec_id)
            return recipes_author


@chefkoch.route('/all-recipes/')
@chefkoch.response(200, 'Results successfully returned')
@chefkoch.response(400, 'Recipes not found')
class AllRecipes(Resource):
    def get(self):
        with driver.session() as session:
            recipes = session.write_transaction(get_all_recipes)
            return recipes


if __name__ == "__main__":
    flask_app.run(debug=True)