# local development guide

1. run local von network/ledger
2. run local did resolver
3. run compiled business partner stack
4. run agent/wallet for local running backend/frontend


### Local Von Network

1. open new terminal
2. clone [von-network](https://github.com/bcgov/von-network.git)
3. build the image
4. start the network/ledger

```shell script
git clone https://github.com/bcgov/von-network.git
cd von-network
./manage build
./manage start --logs
```

Go to [http://localhost:9000](http://localhost:9000) and ensure the ledger is up and all 4 nodes are running correctly.

### Local DID Resolver
We need to stand up a Universal DID Resolver so all Business Partner Agents can find each other and create connections. In this case, it will not be "universal", but will find DIDs on our local ledger. 

1. open a new terminal
2. navigate to [resolver](./resolver)
3. get the genesis transactions from our ledger
4. start the resolver

```shell script
cd ./resolver
curl http://localhost:9000/genesis -o localhost_9000.txn
docker-compose up
```

Now you have a "Universal" DID Resolver at [http://localhost:7776](http://localhost:7776). 

### Build and deploy a Partner
To build up a "network" for our local development, we can build and run a full implementation of our Business Partner. We will connect the current infrastructure using `host.docker.internal`; linux users may have to uncomment the `extra-hosts` in the [compose file](./partner/docker-compose.yml)

#### Build image
1. open new terminal
2. navigate to [bb-pacman](../../../bb-pacman)
3. build the image, tag for local

```shell script
cd ../../../bb-pacman
docker build -t ghcr.io/hyperledger-labs/business-partner-agent:local .
```

#### Deploy Business Partner Agent
1. navigate to [partner](./partner)
2. create an environment file
3. register DID on ledger
4. run the Business Partner Agent

```shell script
cd ./partner
cp .env-example .env
LEDGER_URL=http://localhost:9000 SRC_FILE=$(pwd)/.env-example DEST_FILE=$(pwd)/.env ../../register-did.sh
cp ../../acapy-static-args.yml .
docker-compose up
```

Go to [http://localhost:18080](http://localhost:18080), login using `admin/changeme`.  
Copy your agent's DID and try the resolver:

```shell script
curl -X GET http://localhost:7776/1.0/identifiers/did:sov:LjXHs5EemopowzXUuSRwY5
```

Now, you have a ledger, DID resolver and a full Business Partner Agent.

### Build and Deploy Agent/Wallet
For local development, we need to stand up our aca-py agent and wallet that our Business Partner will use.

1. open new terminal
2. navigate to [agent](./agent)
3. create an environment file
4. register DID on ledger
5. run the agent only

```shell script
cd ./agent
cp .env-example .env
LEDGER_URL=http://localhost:9000 SRC_FILE=$(pwd)/.env-example DEST_FILE=$(pwd)/.env ../../register-did.sh
cp ../../acapy-static-args.yml .
docker-compose up aca-py4 postgres4
```

### Build Local Backend/Frontend

1. build the [frontend code](../../frontend) (Vue application)
2. update local dev environment files
3. 

```shell script
cd ../../frontend
npm run build:development
```

Update business-partner-agent resources/application-dev.yml static-resources to point to your frontend code dist folder.

Example:
```yaml
micronaut:
  security:
    enabled: false
  router:
    # note also check the AppController
    static-resources:
      frontend:
        paths: file:/Users/jason/Projects/parc-jason/mines-digital-trust/services/bb-pacman/frontend/dist
        mapping: /**
```

```shell script
cd ../../backend
mvn install
mvn compile
```

### Run Local Backend/Frontend
This could be very dependent on your IDE and development process. Basically, we want to launch the locally configured Micronaut server, connected to our agent/wallet and serving our local frontend dist.  

You can use the [docker-compose.yml](./agent/docker-compose.yml) as reference, you will need to set JAVA_OPTS and environment variables like you would for Docker. The CLASSPATH is massive and will include all those maven jars.  

Use `host.docker.internal` since you will be using a mix of docker hosted containers (agent and wallet) and your host machine (backend/frontend). 

Example:
```shell script
# set your environment variables...
export BPA_WEB_MODE=false
export BPA_RESOLVER_URL=http://host.docker.internal:7776
export BPA_LEDGER_BROWSER=http://host.docker.internal:7776
export BPA_DID_PREFIX=did:sov:
export BPA_BOOTSTRAP_UN=admin
export BPA_BOOTSTRAP_PW=changeme
export ACAPY_ENDPOINT=http://host.docker.internal:48030
export AGENT_NAME=Dev BPA
# pass in your JAVA_OPTS
java -Dbpa.acapy.url=http://host.docker.internal:48031 -Dmicronaut.security.enabled=true -Dmicronaut.server.port=48080 -Dbpa.pg.url=jdbc:postgresql://host.docker.internal:45432/walletuser -Dbpa.pg.username=walletuser -Dbpa.pg.password=walletpassword -Dbpa.host=host.docker.internal:48080 -Dbpa.https=http -Dmicronaut.environments=dev -classpath <YOUR-PROJECT-CLASSPATH> org.hyperledger.bpa.Application
```

Check your IDE for launching and setting breakpoints.  

Go to [http://localhost:48080](http://localhost:48080), login using `admin/changeme`. Use Business Partners to lookup your other BPA. 

### Stopping
You can stop all the components and leave the data intact so you can bring it back up again without having to re-build and re-seed data.

Open a new terminal for each container (`von-network`, `resolver`, `partner`, `agent`), and call `docker-compose down`.

### Tearing down
If you no longer want your ledger and agents, or want to start from scratch... 

Open a new terminal for each container (`von-network`, `resolver`, `partner`, `agent`), and call `docker-compose down -v --remove-orphans`.  

This will not only stop the containers, but will remove the volumes (where the data is stored). Anytime your remove the agent's data, you will need to register a new DID. Similarly, if you tear down the ledger, you will need to register new DIDs for your agents and reset AND you will need to refresh your DID resolver transactions. 


## Future
Coming soon - how to stand up and debug your local development BPA using Docker - setting breakpoints and hot reloading the BPA inside a running Docker container.



