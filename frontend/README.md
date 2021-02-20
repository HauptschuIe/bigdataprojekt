# React App

Displays our frontend with all the neccessary functions. It was created with the help of react and material-ui. The App connects with a flask API to the neo4j database.

---

#### Setting up the React App

Create the react-app

    npx create-react-app frontend

Delete all non essential files

    App.test.js
    index.css
    logo.svg
    serviceWorker.js
    setupTests.js

Delete all imports and uses of these files in the App.js and index.js

App.js:

    import logo from './logo.svg';

    function App() {
    return (
    [...]
    <img src={logo} className="App-logo" alt="logo" />
    [...]

index.js:

    import "./index.css";
    import * as serviceWorker from "./serviceWorker";

    [...]
    serviceWorker.unregister();

Add the correct path to the gitignore file in your project

    frontend/node_modules

Start your react-app

    npm start

#### Set up a fake-backend

Implement a fake-backend to mimic the access to the api

    npm install -g yo
    npm install -g generator-http-fake-backend

Generate the fake-backend (inside of a new folder)

    yo http-fake-backend

Add the node_modules of your fake backend to the gitignore file

    frontend/http-fake-backend/node_modules

Generate endpoints

    yo http-fake-backend:endpoint

Create a json file in the folder "/http-fake-backend/response-files" for the data your endpoint should return

Example:

    [
     {
        "name": "Köstliche BBQ Spareribs für Smoker und Backofen mit Soße und Gewürzmischung",
        "id": "2338561372249308",
        "category": "Barbecue & Grill",
        "ingredients": [
            "Zucker",
            "Paprikapulver",
            "Salz",
            "Pfeffer",
            "Paprikapulver",
            "Paprikapulver",
            "Chilipulver",
            "Zwiebelpulver",
            "Knoblauchpulver",
            "Orangensaft",
            "Whiskey (Jack Daniels)",
            "Ketchup",
            "Worcestersauce",
            "Marinade (von dem Rub)",
            "Honig",
            "BBQ-Sauce",
            "Zucker",
            "Rippchen (Loin Ribs), 6 kg = 12 Stränge Rippchen"
        ],
        "keywords": ["Hauptspeise", "Sommer", "Party", "Schwein", "Grillen"]
     },
    ]

Configure your Endpoint in Config file "http-fake-backend/server/api/fake-backend-config.js

Example:

    "use strict";

    const SetupEndpoint = require("./setup");

    module.exports = SetupEndpoint({
      name: "recommendationAlogorithm",
      urls: [
          {
                params: "/recipes",
                requests: [
                    {
                        method: "GET",
                        response: "/response-files/recipes.json",
                    },
                ],
          },
       ],
    });

Start your fake-backend

    npm start

Open the link in the terminal to check if everything works fine

#### Testing

Start yor fake-backend

    npm run start:dev

Start your react-app

    npm start

Test all functions of your app

#### Sources

https://github.com/micromata/generator-http-fake-backend

https://reactjs.org/docs/create-a-new-react-app.html

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/frontend.png" width="400" height="200">

#### Deployment

Create a build directory with a production build of the react app

    npm run build

Create a directory containing the Dockerfile and the production build.
Create Nginx docker Image and start an instance of the image.

    docker build -t nginx .
    docker run --name nginx -d -p 8080:80 nginx
