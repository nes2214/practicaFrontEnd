# Vite

Este proyecto corresponde a la actividad: <https://xtec.dev/python/vite/>

En Gitlab tienes una imagen docker de la apliacación: <https://gitlab.com/xtec/python/vite/container_registry>.

Puedes ejecutar la app con docker:

```sh
$ curl -L sh.xtec.dev/docker.sh | sh
$ docker run --rm -p 80:80 registry.gitlab.com/xtec/python/vite
```

## Develop

Arranca el servidor Python:

```sh
$ poetry update
$ bun run server
```

Arranca el servidor Vite para React:

```sh
 deno install --allow-scripts=npm:@swc/core
```

```sh
$ bun update
$ bun run client
```

Abre el navegador en <http://localhost:3000/>

Puedes construir una imagen con el nombre `app`:

```sh
$ docker build --tag app .
$ docker run -p 80:80 app
```

Pudes entrar dentro de la aplicación para debug:

```sh
$ docker run --rm -it app /bin/sh
```
