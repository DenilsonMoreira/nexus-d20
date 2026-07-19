# ADR 0005 — Sessões autenticadas

## Status

Aceita em 18 de julho de 2026.

## Contexto

A aplicação web precisa autenticar usuários sem expor credenciais a JavaScript e deve permitir revogação e rotação de sessões.

## Decisão

Usar Argon2 para senhas, JWT curto para acesso e token opaco para atualização. Ambos são transportados em cookies HTTP-only. O token opaco é armazenado somente como SHA-256, possui expiração, é rotacionado em cada atualização e pode ser revogado no logout.

## Consequências

- Tokens não precisam ser persistidos no armazenamento do navegador acessível a scripts.
- Vazamento do banco não revela tokens de atualização utilizáveis.
- A rotação limita reutilização de tokens antigos.
- Produção exige HTTPS para ativar cookies `Secure`.
