## Python - Vite

This project corresponds to the activity: https://xtec.dev/python/vite/

A Docker image of the application is available on GitLab:
https://gitlab.com/xtec/python/vite/container_registry

You can run the app directly with Docker:

```sh
docker run --rm -p 80:80 registry.gitlab.com/xtec/python/vite
```

## Develop

Start the Python server:

```sh
deno task server
```

Install client dependencies:

```sh
deno install --allow-scripts=npm:@swc/core
```

Start the Vite development server:

```sh
 deno task client
```

Then open your browser at: http://localhost:3000/

## Docker

You can build a Docker image named app:

```sh
docker build --tag app .
docker run -p 80:80 app
```

You can also start a shell inside the container for debugging:

```sh
$ docker run --rm -it app /bin/sh
```
