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
- `docker compose up --build -d`: inconclusivo neste ambiente; o download das imagens excedeu dez minutos e nenhum container foi criado.
- O aceite da Fase 0 permanece pendente até todos os health checks ficarem saudáveis.

## Ferramentas locais

- A instalação das dependências Python e Node excedeu o limite do ambiente.
- As suítes locais não foram reexecutadas nesta rodada; os resultados anteriores permanecem registrados acima, mas não substituem uma nova validação.
- GitHub CLI (`gh`) não está instalado; publicação e abertura de PR permanecem bloqueadas.

## Primeiro teste recomendado na máquina do desenvolvedor

```bash
cp .env.example .env
docker compose config
docker compose up --build
docker compose run --rm api alembic upgrade head
```
