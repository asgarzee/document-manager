# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React based client.  This API/client can be used as a bootstrap to implement the specific features requested in the assessment description. 

## Documentation
#### You can find High level Design Document at /docs/HLD.md

## Getting Started
## Tech Stack

**Server:** Django, SQLite

### Client Development 
The client project is a [Create React App](https://create-react-app.dev/) that has been tested against [Node v18.19.0 Hydrogen LTS](https://nodejs.org/download/release/v18.19.0/).  An [.nvmrc](https://github.com/nvm-sh/nvm#calling-nvm-use-automatically-in-a-directory-with-a-nvmrc-file) file has been included so that the command `$ nvm use` should select the correct NodeJS version through NVM.
1. Navigate to the client/doc-manager directory.
2. `$ npm install` to install the dependencies.
3. `$ npm start` to start the React development server.

## Initial Setup

### 1. Install Docker
Follow link to install [Docker](https://www.docker.com/products/docker-desktop/) https://www.docker.com/products/docker-desktop/

### 2. Create two directories media and static 
```shell
cd document-manager
mkdir src/propylon_document_manager/media src/propylon_document_manager/static
```

###3. Build Django Server
```shell
docker compose up
```
Server will be serving at http://0.0.0.0:8001/

###4. Create a User to start with the APIs
```shell
make createsuperuser
```


## Following are some useful commands
#### Run a User
```shell
make createsuperuser
```

#### Run Migrations
```shell
make make-migrations
```

#### Run Tests
```shell
make test
```

#### Reformat Code
```shell
make format
```

#### Reformat Code
```shell
make format
```

#### Check Linting Issues
```shell
make lint
```

#### Fix Linting Issues
```shell
make lint-fix
```
