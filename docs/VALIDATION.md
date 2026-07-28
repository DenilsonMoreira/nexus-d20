# Relatório de validação

## Versão 1.0.1 — 28 de julho de 2026

### Jornadas verificadas no navegador

- Cadastro, sessão persistida, logout e novo login.
- Criação de campanha e primeira ficha por um mestre.
- Edição persistida e auditada de atributos da ficha.
- Geração de convite de jogador pelo mestre.
- Cadastro de um segundo usuário, aceite do convite e criação da própria ficha.
- Edição da ficha pelo jogador sem exposição da Central do Mestre.
- Retorno do mestre, listagem dos participantes e troca para a ficha do jogador.
- Swagger em `http://localhost:8200/docs`, com OpenAPI e rotas renderizados.
- Layout desktop e breakpoint móvel 390×844, incluindo editor e navegação inferior.

### Regressão automatizada

- Frontend: ESLint, TypeScript, Vitest e build de produção.
- Backend: Ruff, Mypy e suíte completa de Pytest.
- Segurança: auditorias npm e Python.
- Infraestrutura: validação do Docker Compose e health checks.

---

# Validação da fundação

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
