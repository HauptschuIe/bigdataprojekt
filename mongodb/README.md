# MongoDB

Stores recipes from the Webscraper in a MongoDB cluster

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/mongodb.png" width="400" height="300">

## Sharded MongoDB Cluster:

**Shard:** Each shard contains a subset of the sharded data. Each shard can be deployed as a replica set.

**Mongos (router):** The mongos acts as query routers, providing an interface between client applications and the sharded cluster.

**Config servers:** Config servers store metadata and configuration settings for the cluster.

## Getting Started

create the containers

    docker-compose up -d

configure the config servers replica set

    docker exec -it mongocfg1 bash -c "echo 'rs.initiate({_id: \"mongors1conf\",configsvr: true, members: [{ _id : 0, host : \"mongocfg1\" },{ _id : 1, host : \"mongocfg2\" }, { _id : 2, host : \"mongocfg3\" }]})' | mongo"

initiate the shard replica set

    docker exec -it mongors1n1 bash -c "echo 'rs.initiate({_id : \"mongors1\", members: [{ _id : 0, host : \"mongors1n1\" },{ _id : 1, host : \"mongors1n2\" },{ _id : 2, host : \"mongors1n3\" }]})' | mongo"

connect shard to the routers

    docker exec -it mongos1 bash -c "echo 'sh.addShard(\"mongors1/mongors1n1\")' | mongo "

create a Database named chefkoch

    docker exec -it mongors1n1 bash -c "echo 'use chefkoch' | mongo"

eneable sharding

    docker exec -it mongos1 bash -c "echo 'sh.enableSharding(\"chefkoch\")' | mongo "

create a collection named recipes on the sharded database

    docker exec -it mongors1n1 bash -c "echo 'db.createCollection(\"chefkoch.recipes\")' | mongo "

eneable sharding on the collection

    docker exec -it mongos1 bash -c "echo 'sh.shardCollection(\"chefkoch.recipes\", {\"shardingField\" : 1})' | mongo "


----

Sources:

https://dzone.com/articles/composing-a-sharded-mongodb-on-docker

https://docs.mongodb.com/manual/core/sharded-cluster-components/
