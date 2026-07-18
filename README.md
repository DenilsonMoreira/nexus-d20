# Nexus d20

Plataforma web para centralizar fichas, evolução de personagens, magias, inventário, durabilidade, viagens e preparação de campanhas de RPG usando **D&D 5e — regras de 2014** como base, com regras personalizáveis pelo mestre.

> Estado atual: fundação executável do produto e especificação fechada do MVP para desenvolvimento pelo Codex.

## Visão do produto

O Nexus d20 possui duas experiências principais:

- **Jogador:** ficha inteligente, evolução guiada, atributos e modificadores, magias, inventário, peso, ataques, durabilidade, notas e imagens.
- **Mestre:** edição de fichas, grupo ativo, descansos, biblioteca de itens/magias/condições/preços, bestiário, encontros por bioma, teia de conhecimento e painéis personalizados.

O motor de regras é determinístico. IA pode explicar e sugerir decisões no futuro, mas não será a fonte da verdade para cálculos.

## Stack

- Front-end: Next.js 16, React 19, TypeScript e App Router.
- API: FastAPI, Python 3.13 e Pydantic 2.
- Banco: PostgreSQL 18.
- Arquivos: MinIO local, compatível com S3 em produção.
- Cache e eventos futuros: Redis.
- Desenvolvimento e produção: Docker Compose.
- CI: GitHub Actions.

## Início rápido com Docker

```bash
cp .env.example .env
docker compose up --build
```

Serviços:

- Aplicação: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

Credenciais locais padrão estão em `.env.example`. Troque todas antes de publicar.

## Comandos úteis

```bash
make up            # inicia o ambiente
make down          # encerra o ambiente
make logs          # acompanha logs
make test          # testes do motor e front-end
make lint          # lint e verificações
make db-migrate    # executa migrações
make db-revision m="descrição"  # cria migração
```

## Execução sem Docker

### API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

### Front-end

```bash
cd frontend
npm install
npm run dev
```

## Estrutura

```text
nexus-d20/
├── AGENTS.md
├── ROADMAP.md
├── DECISIONS.md
├── compose.yaml
├── compose.prod.yaml
├── backend/
├── frontend/
├── docs/
├── infra/
├── scripts/
└── .github/
```

## Documentos obrigatórios para o Codex

Leia nesta ordem:

1. `AGENTS.md`
2. `docs/PRODUCT_SPEC.md`
3. `docs/RULES_ENGINE.md`
4. `docs/PERMISSIONS.md`
5. `docs/DATA_MODEL.md`
6. `ROADMAP.md`
7. `DECISIONS.md`

## Conteúdo de D&D

O produto usa o SRD 5.1 como referência pública permitida para D&D 5e de 2014. Não inclua conteúdo de livros não presentes no SRD em seeds públicos. Consulte `docs/CONTENT_AND_LICENSE.md`.

## GitHub

O repositório já possui Git, CI, templates e Dependabot configurados. Para publicar:

```bash
git remote add origin git@github.com:SEU_USUARIO/nexus-d20.git
git push -u origin main
```

Consulte `docs/GITHUB_SETUP.md`.
