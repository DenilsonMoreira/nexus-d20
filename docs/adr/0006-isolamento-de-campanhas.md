# ADR 0006 — Isolamento de campanhas

## Status

Aceita em 19 de julho de 2026.

## Contexto

IDs UUID reduzem adivinhação, mas não substituem autorização. Campanhas precisam garantir isolamento multi-tenant e convites não podem permitir entrada de contas diferentes do destinatário.

## Decisão

Consultar participação em toda rota que recebe `campaign_id`. Retornar 404 para não membros e 403 para membros sem papel suficiente. Convites usam token opaco armazenado como hash, expiram em sete dias e exigem correspondência exata com o e-mail autenticado. O proprietário é mestre protegido. A operação de exclusão arquiva a campanha.

## Consequências

- IDs enviados pelo cliente não são tratados como autorização.
- A API reduz vazamento sobre existência de campanhas.
- Tokens vazados do banco não podem ser usados diretamente.
- Campanhas arquivadas permanecem recuperáveis por uma operação administrativa futura.
