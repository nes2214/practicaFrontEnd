## Python - Vite

Este proyecto corresponde a la actividad: <https://xtec.dev/python/vite/>

En Gitlab tienes una imagen docker de la apliacación: <https://gitlab.com/xtec/python/vite/container_registry>.

Puedes ejecutar la app con docker:

```sh
docker run --rm -p 80:80 registry.gitlab.com/xtec/python/vite
```

## Develop

Arranca el servidor Python:

```sh
$ deno task server
```

Arranca el servidor Vite para React:

```sh
 deno install --allow-scripts=npm:@swc/core
 deno task client
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
