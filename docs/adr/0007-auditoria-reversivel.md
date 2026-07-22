# ADR 0007 — Auditoria reversível

## Status

Aceita em 22 de julho de 2026.

## Contexto

Alterações administrativas e mecânicas precisam ser rastreáveis e, quando seguro, reversíveis sem apagar o histórico ou sobrescrever mudanças posteriores.

## Decisão

Gravar auditoria na mesma transação da alteração de domínio. Cada evento registra antes/depois, responsável e motivo quando aplicável. Eventos reversíveis são marcados explicitamente. Uma reversão exige mestre, motivo e estado atual compatível; marca o evento original e cria outro evento ligado por `reversal_of_id`. A primeira operação com reversão automática é o arquivamento de campanha.

## Consequências

- Falha na auditoria também desfaz a alteração de domínio.
- O histórico original permanece imutável e consultável.
- Reversões repetidas ou sobre estado divergente são bloqueadas.
- Novos tipos de reversão exigem implementação e testes específicos; não existe reversão genérica presumida.
