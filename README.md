# Python - Vite

This project corresponds to the activity: https://xtec.dev/python/vite/

### TODO run app directly

A Docker image of the application is available on GitLab:
https://gitlab.com/xtec/python/vite/container_registry

You can run the app directly with Docker:

```sh
docker run --rm -p 80:80 registry.gitlab.com/xtec/python/vite
```

## Develop

El repte és arrencar aquest projecte, que connecta el front-end de React (vite) amb el back-end (Python, FastAPI, PostgreSQL):

### 1. Pots clonar-lo al teu repositori.

```sh
git clone https://gitlab.com/xtec/python/vite/
```

Obre el projecte amb VSCODE:

```sh
code .
```

### 2. Arrenca el projecte amb wsl des de VSCode

https://xtec.dev/windows/wsl

>< WSL UBUNTU

### 3. Instal·lar Docker dins d'wsl si no el teniu.

```sh
curl -L sh.xtec.dev/docker.sh | sh
```

Font (no cal)
    https://onthedock.github.io/post/170410-docker-engine_vs_docker.io/

Recomanem extensió Docker per VSCode. 

https://gitlab.com/xtec/python/vite/-/blob/main/README.md?ref_type=heads

### 4. Usar docker per a tenir una BBDD en PostgreSQL

```sh
docker run -d --name postgres --restart=always -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=postgres postgres:18
```

Observació! Si ja teniu un contenidor que es diu postgres, renombreu-lo a postgres2 o pareu-lo.

Hauriem de provar la base de dades, tal i com vau veure:
    https://xtec.dev/data/postgres/basic
    
Als fitxers .env i a .gitlab.ci hi ha el nom i les credencials de la base de dades:

  POSTGRES_DB: clinic

Si voleu posar doctors:
    
```sh
docker exec -it postgres bash
psql -U postgres
```

```sql
INSERT INTO doctors (username, name) VALUES
('drhouse', 'Gregory House'),
('drcuddy', 'Lisa Cuddy'),
('drwilson', 'James Wilson');
```

O millor encara, llegiu com posar un fitxer sql al contenidor (todo)

```sh 
wget https://gitlab.com/xtec/postgres-data/-/raw/main/scott.sql
docker cp scott.sql postgres:scoot.sql
cat scott.sql | docker exec -i postgres su postgres -c "psql"
```

### 5. Instal·lar deno

```sh
   https://docs.deno.com/runtime/getting_started/installation/
   
   sudo apt update
   sudo apt install unzip -y
   curl -fsSL https://deno.land/install.sh | sh
```

   Caldrà reiniciar Code i wsl

Si trobem passos adicionals necessaris ho actualitzarem al readme.md

### 6. Executar deno per muntar el server (Python)

Primer, instal·la uv:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

Ara si, arrenca el server:

```sh
deno task server
```

### 7. Client

Install client dependencies:
    
```sh
deno install --allow-scripts=npm:@swc/core
```

Start the Vite development server:

```sh 
 deno task client
```

## TODO - Docker image

You can build a Docker image named app:

```sh
docker build --tag app .
docker run -p 80:80 app
```

You can also start a shell inside the container for debugging:

```sh
$ docker run --rm -it app /bin/sh
```
