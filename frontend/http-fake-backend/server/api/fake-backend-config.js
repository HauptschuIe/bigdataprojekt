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
