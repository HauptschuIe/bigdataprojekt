# Neo4j

Neo4j is a graph database management system

## Overview

<img src="https://github.com/helenanebel/bigdataproject/blob/master/images/neo4j.png" width="400" height="300">

## Setting up the Neo4j cluster

Set up a Causal Cluster with Neo4j running in a Docker container.

```
docker network create --driver=bridge cluster

docker run --name=core1 --detach --network=cluster \
    --publish=7474:7474 --publish=7473:7473 --publish=7687:7687 \
    --hostname=core1 \
    --env NEO4J_dbms_mode=CORE \
    --env NEO4J_causal__clustering_expected__core__cluster__size=3 \
    --env NEO4J_causal__clustering_initial__discovery__members=core1:5000,core2:5000,core3:5000 \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --env NEO4J_dbms_connector_bolt_advertised__address=localhost:7687 \
    --env NEO4J_dbms_connector_http_advertised__address=localhost:7474 \
    neo4j:4.1-enterprise

docker run --name=core2 --detach --network=cluster \
    --publish=8474:7474 --publish=8473:7473 --publish=8687:7687 \
    --hostname=core2 \
    --env NEO4J_dbms_mode=CORE \
    --env NEO4J_causal__clustering_expected__core__cluster__size=3 \
    --env NEO4J_causal__clustering_initial__discovery__members=core1:5000,core2:5000,core3:5000 \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --env NEO4J_dbms_connector_bolt_advertised__address=localhost:8687 \
    --env NEO4J_dbms_connector_http_advertised__address=localhost:8474 \
    neo4j:4.1-enterprise

docker run --name=core3 --detach --network=cluster \
    --publish=9474:7474 --publish=9473:7473 --publish=9687:7687 \
    --hostname=core3 \
    --env NEO4J_dbms_mode=CORE \
    --env NEO4J_causal__clustering_expected__core__cluster__size=3 \
    --env NEO4J_causal__clustering_initial__discovery__members=core1:5000,core2:5000,core3:5000 \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --env NEO4J_dbms_connector_bolt_advertised__address=localhost:9687 \
    --env NEO4J_dbms_connector_http_advertised__address=localhost:9474 \
    neo4j:4.1-enterprise
```
Add two Read Replica instances
```
docker run --name=read-replica1 --detach --network=cluster \
         --publish=10474:7474 --publish=10473:7473 --publish=10687:7687 \
         --hostname=read-replica1 \
         --env NEO4J_dbms_mode=READ_REPLICA \
         --env NEO4J_causal__clustering_initial__discovery__members=core1:5000,core2:5000,core3:5000 \
         --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
         --env NEO4J_dbms_connector_bolt_advertised__address=localhost:10687 \
         --env NEO4J_dbms_connector_http_advertised__address=localhost:10474 \
         neo4j:4.1-enterprise
         
docker run --name=read-replica1 --detach --network=cluster \
         --publish=11474:7474 --publish=11473:7473 --publish=11687:7687 \
         --hostname=read-replica1 \
         --env NEO4J_dbms_mode=READ_REPLICA \
         --env NEO4J_causal__clustering_initial__discovery__members=core1:5000,core2:5000,core3:5000 \
         --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
         --env NEO4J_dbms_connector_bolt_advertised__address=localhost:11687 \
         --env NEO4J_dbms_connector_http_advertised__address=localhost:11474 \
         neo4j:4.1-enterprise
```

#### Change password
Set password in docker run commmand "--env NEO4J_AUTH=neo4j/test \" or or change manually when connect to Cypher-Shell for the first time.

#### Testing

Cypher Shell:
```
docker exec -it <container> bash
cypher-shell -u <username> -p <password>
```
Show cluster:
```
CALL dbms.cluster.overview();
```
Print all rows
```
MATCH (n) OPTIONAL MATCH (n)-[r]-() RETURN n, r;
```
----

Sources:

https://neo4j.com/docs/operations-manual/current/docker/clustering/

https://neo4j.com/docs/operations-manual/current/manage-databases/queries/
