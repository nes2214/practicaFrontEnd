# Vite

Aquest projecte correspon a l'activitat: <https://xtec.dev/python/vite/>


A `registry.gitlab.com`  tens una imatge del projecte.

La pots executar amb docker:

```sh
$ curl -L sh.xtec.dev/docker.sh | sh
$ docker run --rm -p 80:80 registry.gitlab.com/xtec/python/vite
```

## Develop

Executa el servidor Python:

```sh
$ poetry shell
$ poetry install
$ bun run server
```

Executa el client React:

```sh
$ bun install
$ bun run client
```

Obre el navegador a <http://localhost:3000/>

Pots contstruir una imatge "Docker":

```sh
$ docker build --tag vite .
$ docker run -p 80:80 vite
```

Si debug:

```sh
$ docker run --rm -it vite /bin/sh
```
