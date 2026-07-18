# Relatório de validação da fundação

Data: 18 de julho de 2026.

## Back-end

- Ruff: aprovado.
- Mypy estrito: aprovado.
- Pytest: 15 testes aprovados.
- Compileall: aprovado.
- Smoke test dos endpoints de ataque e carga: HTTP 200 e resultados esperados.

## Front-end

- npm audit: zero vulnerabilidades conhecidas no lock atual.
- ESLint: aprovado.
- TypeScript: aprovado.
- Vitest: aprovado.
- Build Next.js de produção: aprovado.

## Infraestrutura

- YAML do Compose, CI, Dependabot e templates: parse aprovado.
- Volume do PostgreSQL 18 configurado em `/var/lib/postgresql`.
- Docker não estava disponível no ambiente de criação; portanto, os containers não foram iniciados nesta validação.

## Primeiro teste recomendado na máquina do desenvolvedor

```bash
cp .env.example .env
docker compose config
docker compose up --build
docker compose run --rm api alembic upgrade head
```
