# ADR 0008 — Recuperação de acesso

## Status

Aceita em 22 de julho de 2026.

## Contexto

Usuários precisam recuperar acesso sem permitir enumeração de contas, reutilização de links ou manutenção de sessões comprometidas após a troca de senha.

## Decisão

Emitir token opaco aleatório, armazenar somente seu SHA-256, limitar a validade a 30 minutos e aceitar cada token uma vez. A solicitação pública sempre retorna a mesma resposta. Ao redefinir a senha, revogar refresh tokens e incrementar `auth_version`, invalidando JWTs anteriores. Entregar por SMTP; usar Mailpit versionado apenas em desenvolvimento.

## Consequências

- O banco não contém tokens de recuperação diretamente utilizáveis.
- A resposta da API não confirma a existência de um e-mail.
- Trocar a senha encerra todas as sessões existentes.
- Produção depende de SMTP configurado e monitorado.
