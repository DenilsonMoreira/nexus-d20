# Arquitetura do Nexus d20

## Visão geral

O Nexus d20 é um monorepo dividido em aplicação web, API, armazenamento relacional, cache e objetos. A separação por domínio permite que o motor de regras seja utilizado pela API, por jobs futuros e por testes sem depender da interface.

```text
Navegador
   │
   ▼
Next.js ─────► FastAPI ─────► PostgreSQL
                  │              │
                  ├──────────► Redis
                  └──────────► S3/MinIO
```

## Fronteiras

### Front-end

Responsável por apresentação, formulários, acessibilidade, estados locais e chamadas à API. Não é fonte da verdade para regras, permissões ou segredos.

### API

Responsável por autorização, regras, validação, auditoria, transações e geração de URLs assinadas.

### Motor de regras

Módulos puros em `backend/app/domain/rules`. Não acessam banco diretamente. Recebem snapshots e devolvem resultados que podem ser simulados ou aplicados.

### Persistência

PostgreSQL armazena entidades, versões, overrides, eventos e auditoria. Redis será usado para cache, rate limiting, idempotência e eventos efêmeros. Objetos ficam em S3 compatível.

## Estratégia de módulos

- `identity`: usuários, sessões e convites;
- `campaigns`: campanhas, membros e regras;
- `characters`: ficha, evolução e recursos;
- `compendium`: itens, magias, condições, preços e criaturas;
- `inventory`: instâncias, peso, durabilidade e transferências;
- `combat`: ataques, iniciativa e encontros;
- `travel`: biomas, deslocamento, recursos e fadiga;
- `notes`: notas, compartilhamento e mídia;
- `gm`: teia, linha do tempo, painéis e segredos;
- `audit`: eventos, reversões e idempotência.

## Escala futura

O monorepo não implica deploy monolítico. Web, API, worker, banco, Redis e objetos podem ser movidos para serviços gerenciados independentemente.
