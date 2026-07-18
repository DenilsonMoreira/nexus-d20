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
- A referência inválida do MinIO foi substituída por uma versão oficial existente.
- `docker compose config --quiet`: aprovado com o arquivo `.env` local.
- O lockfile não contém referências a registros privados e a imagem web instala com `npm ci`.
- Portas publicadas no host podem ser configuradas pelo `.env` sem alterar portas internas.
- `docker compose up --build -d --wait`: aprovado.
- PostgreSQL, Redis, MinIO, API e web: saudáveis.
- Inicialização do bucket MinIO: concluída com sucesso.
- `alembic upgrade head`: aprovado em banco vazio.
- `alembic check`: nenhuma operação nova detectada.
- Critério de aceite da Fase 0: concluído.

## Ferramentas locais

- Validações foram executadas dentro das imagens Docker reproduzíveis.
- Publicação é realizada diretamente com `git`, conforme o fluxo do projeto.

## Primeiro teste recomendado na máquina do desenvolvedor

```bash
cp .env.example .env
docker compose config
docker compose up --build
docker compose run --rm api alembic upgrade head
```
