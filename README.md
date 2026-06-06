# Personal Finance API

API para controle financeiro pessoal desenvolvida com Django, Django REST Framework, PostgreSQL e Docker.

## Status

MVP inicial da API com autenticacao, categorias, carteiras, transacoes, resumo mensal e documentacao OpenAPI.

## Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Docker Compose
- django-environ
- django-cors-headers
- drf-spectacular
- Simple JWT
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

Rode as migrations:

```bash
docker compose -f docker-compose.dev.yml run --rm api python manage.py migrate
```

Crie seu usuario local:

```bash
docker compose -f docker-compose.dev.yml run --rm api python manage.py createsuperuser
```

Se a porta `8000` estiver ocupada, altere `API_PORT` no `.env` e acesse a porta configurada.

## URLs úteis

```txt
http://localhost:8000/api/health/
http://localhost:8000/api/docs/
http://localhost:8000/api/schema/
```

## Testes

```bash
docker compose -f docker-compose.dev.yml run --rm api pytest
```
