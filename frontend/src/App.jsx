import React from "react";
import "./App.css";
import { BrowserRouter as Switch, Route, Router } from "react-router-dom";
import { createBrowserHistory } from "history";
import AllRecipes from "./pages/AllRecipes";
import About from "./pages/About";
import Header from "./components/header.component";
import RecBasedOnIngredients from "./pages/RecBasedOnIngredients";
import RecipesByName from "./pages/RecipesByName";
import RecBasedOnUserRatings from "./pages/RecBasedOnUserRatings";
import RecipesFromAuthor from "./pages/RecipesFromAuthor";

/**
 *
 * App component of our App to route to every page
 *
 * @author [Lukas Rutkauskas] (https://github.com/LukasRutkauskas)
 * @author [Jonas Wagenknecht] (http://github.com/Hauptschule)
 */

const history = createBrowserHistory();

class App extends React.Component {
  render() {
    return (
      // Routing for the pages
      <Router history={history}>
        <div className="App">
          <Switch>
            <Header />
            <Route path="/" exact component={AllRecipes} />
            <Route path="/recipes-by-name" component={RecipesByName} />
            <Route
              path="/recipes-from-an-author"
              component={RecipesFromAuthor}
            />
            <Route
              path="/recommendations-based-on-user-ratings"
              component={RecBasedOnUserRatings}
            />
            <Route
              path="/recommendations-based-on-ingredients"
              component={RecBasedOnIngredients}
            />
            <Route path="/about" component={About} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
