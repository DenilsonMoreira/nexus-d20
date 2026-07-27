# Implantação e checklist de produção

## Ambientes

Desenvolvimento usa `compose.yaml`. Homologação e produção usam
`compose.prod.yaml`, imagens construídas do mesmo commit e ambientes protegidos
do GitHub. O workflow `Homologation` valida o Compose e implanta manualmente
somente após aprovação do ambiente `homologation`.

Segredos exigidos na homologação:

- `STAGING_HOST`, `STAGING_USER` e `STAGING_PATH`;
- `STAGING_SSH_PRIVATE_KEY`;
- `STAGING_SSH_HOST_KEY`, obtida e conferida fora do workflow.

O host mantém seu `.env` fora do Git com domínio, banco, Redis, S3, SMTP,
`JWT_SECRET`, `METRICS_TOKEN`, CORS e limites. `TRUST_PROXY_HEADERS=true` só é
permitido quando a API recebe tráfego exclusivamente do proxy confiável.

## Implantação

```bash
docker compose -f compose.prod.yaml config --quiet
docker compose -f compose.prod.yaml up -d --build
docker compose -f compose.prod.yaml exec -T api alembic upgrade head
curl --fail https://SEU_DOMINIO/health
```

Faça rollback voltando o Git para o commit anterior aprovado e reconstruindo os
serviços. Migrações destrutivas exigem plano específico; a migração atual é
aditiva.

## Backup e restauração

Agende `scripts/backup.sh` diariamente com cópia cifrada fora da VPS. O pacote
contém dump PostgreSQL, objetos e checksums. O padrão conserva 30 dias.

Teste mensalmente em ambiente isolado:

```bash
BACKUP_ROOT=/backup/nexus-d20 scripts/backup.sh
scripts/restore.sh --confirm /backup/nexus-d20/AAAAMMDDTHHMMSSZ
```

`restore.sh` é destrutivo: ele interrompe API/web e recria o banco e os objetos.
Nunca o execute contra produção sem janela aprovada e backup conferido.

## Observabilidade

- logs HTTP estruturados incluem rota, status, latência e `X-Request-ID`, sem payload;
- `/metrics` expõe contadores e latência no formato Prometheus e exige
  `Authorization: Bearer $METRICS_TOKEN`;
- alertar para taxa 5xx, p95 acima de 500 ms, uso de disco, falha de backup,
  indisponibilidade e aumento de respostas 429;
- coletar métricas pela rede interna, pois o Caddy não publica `/metrics`.

## Segurança e retenção

Rate limit usa Redis, com fallback local quando Redis falha. Endpoints de
autenticação possuem limite próprio. O proxy deve manter limite de borda para
ataques distribuídos. Headers CSP, HSTS em produção, `nosniff`, Referrer-Policy
e Permissions-Policy são emitidos pela API.

Executar diariamente:

```bash
docker compose -f compose.prod.yaml exec -T api \
  python -m app.maintenance retention --apply
```

Antes de cada release, CI executa Ruff, mypy, pytest, Bandit, pip-audit,
lint/typecheck/test/build do front-end e npm audit.

## Teste de carga

Com homologação isolada:

```bash
k6 run -e BASE_URL=https://homologacao.exemplo.com tests/load/smoke.js
```

Critérios iniciais: erros abaixo de 1% e p95 abaixo de 500 ms com 20 usuários
virtuais. Resultados devem ser anexados à release; aumentar a carga somente com
monitoramento ativo.

## Checklist de liberação

### Automatizado no repositório

- [x] Compose de produção sem portas públicas para PostgreSQL, Redis e MinIO.
- [x] migrações versionadas e aditivas;
- [x] auditoria de dependências e análise estática na CI;
- [x] rate limit, headers de segurança e cookies seguros em produção;
- [x] métricas, logs correlacionados e health check;
- [x] exportação e exclusão de conta;
- [x] política de retenção executável;
- [x] backup, checksums e restauração documentada;
- [x] termos e privacidade documentados;
- [x] teste de carga reproduzível;
- [x] workflow de homologação com chave de host fixada.

### Evidências externas obrigatórias antes do lançamento público

- [ ] domínio e TLS válidos;
- [ ] segredos fortes e exclusivos carregados no host;
- [ ] SMTP real testado, inclusive recuperação de senha;
- [ ] bucket privado e backup externo cifrado;
- [ ] restauração concluída em ambiente isolado;
- [ ] dashboards e alertas conectados a `/metrics`;
- [ ] resultado do k6 dentro dos limites;
- [ ] revisão jurídica da minuta de termos e privacidade;
- [ ] implantação de homologação aprovada e smoke test registrado.

Os itens externos não devem ser marcados sem evidência. A ausência de qualquer
um deles bloqueia o lançamento comercial, ainda que o código esteja pronto.
