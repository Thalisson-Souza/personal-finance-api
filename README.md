# Personal Finance API

API para controle financeiro pessoal desenvolvida com Django, Django REST Framework, PostgreSQL e Docker.

## Status

Base inicial do projeto criada com endpoint de health check.

## Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Docker Compose
- django-environ
- pytest
- pytest-django

## Como rodar em desenvolvimento

Crie o arquivo de ambiente local:

```bash
cp .env.example .env
```

Suba a API e o banco:

```bash
docker compose -f docker-compose.dev.yml up api
```

Se a porta `8000` estiver ocupada, altere `API_PORT` no `.env` e acesse a porta configurada.

Health check:

```bash
curl http://localhost:8000/api/health/
```

## Testes

```bash
docker compose -f docker-compose.dev.yml run --rm api pytest
```
