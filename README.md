# Vite

Aquest projecte correspon a l'activitat: <https://xtec.dev/python/vite/>

## Docker

Instal.la docker:

```sh
curl -L sh.xtec.dev/docker.sh | sh
```

Executa el contenidor:

```sh
docker run -it registry.gitlab.com/xtec/python/vite
```

## Develop

Executa el servidor Python:

```sh
$ poetry shell
$ poetry install
$ fastapi dev server/main.py
```

Executa el client React:

```sh
$ bun install
$ bun run dev
```

Obre el navegador a <http://localhost:3000/>

### Docker

A l'hora de desenvolupar l'aplicació:

```sh
$ docker build --tag vite .
$ docker run -p 80:80 vite
```

Si debug:

```sh
$ docker run --rm -it vite /bin/sh
```
