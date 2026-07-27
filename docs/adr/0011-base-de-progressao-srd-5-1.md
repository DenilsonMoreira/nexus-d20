# ADR 0011 — Base de progressão SRD 5.1

## Status

Aceita em 26 de julho de 2026.

## Contexto

A Fase 3 precisa iniciar o assistente de subida de nível sem misturar tabela geral, regras específicas de classe, persistência e políticas de campanha. Campanhas também podem usar experiência ou avanço por marco.

## Decisão

Implementar uma camada pura e determinística com os limiares de experiência e bônus de proficiência dos níveis 1 a 20 do SRD 5.1. O nível total do personagem determina o bônus de proficiência.

A primeira simulação considera somente o próximo nível e nunca persiste alterações. Quando recebe XP, informa elegibilidade, XP restante e o maior nível correspondente à quantidade fornecida. Sem XP, retorna `not_evaluated` para deixar a política de avanço por marco sob controle da campanha. O nível 20 retorna `level_cap`.

Efeitos de classe, PV, escolhas, magias e multiclasse serão adicionados como composições explícitas antes da aplicação idempotente e auditada.

## Consequências

- A tabela geral pode ser testada isoladamente e reutilizada por qualquer classe.
- A API não presume que toda campanha usa XP.
- Saltos de vários níveis continuam sendo aplicados um nível por vez.
- Nenhum estado é alterado até que o fluxo completo de simulação e aplicação exista.
