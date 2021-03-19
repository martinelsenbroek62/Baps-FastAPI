# baps-api
**BioPharma Asset Planning Software**


## Development
This project is intended to be developed in Docker and setup already
for vscode devcontainers (see `./.devcontainer`).

The containers can also be built and run using `docker-compose`.
```bash
make build
# create external volume if not exists
docker volume create baps-pg
make up
```
