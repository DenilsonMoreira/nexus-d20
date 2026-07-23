# Implantação

## Desenvolvimento

Use `compose.yaml`.

## Produção inicial

Use `compose.prod.yaml` em uma VPS com:

- domínio configurado;
- firewall;
- volumes persistentes;
- backups externos;
- segredos fortes;
- monitoramento;
- SMTP ou provedor de autenticação configurado.

Para e-mail transacional, configurar `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS` e `MAIL_FROM`. O Mailpit pertence somente ao desenvolvimento e não deve ser publicado em produção. Validar a entrega de recuperação de acesso antes de liberar usuários.

```bash
docker compose -f compose.prod.yaml up -d --build
```

## Antes da publicação

- Trocar todos os segredos.
- Remover exposição direta do PostgreSQL, Redis e MinIO.
- Configurar bucket privado.
- Executar migrações.
- Criar usuário administrador sem senha padrão.
- Configurar backup diário e teste de restauração.
- Adicionar Sentry/OpenTelemetry.
- Configurar rate limiting.
- Revisar CORS e cookies seguros.
- Ativar headers de segurança e CSP.
- Revisar LGPD, termos e exclusão de conta.

## Estratégia futura

A aplicação pode migrar separadamente para:

- front-end gerenciado;
- API em containers;
- PostgreSQL gerenciado;
- S3 compatível;
- Redis gerenciado.

O código não deve depender de particularidades do Docker Compose.

## Armazenamento de objetos

O MinIO do Compose é destinado a desenvolvimento, homologação e instalações privadas controladas. Para um SaaS público, prefira um serviço S3 compatível gerenciado e revise as licenças dos componentes de infraestrutura antes do lançamento.
