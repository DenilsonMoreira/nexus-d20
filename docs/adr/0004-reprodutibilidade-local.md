# ADR 0004 — Reprodutibilidade do ambiente local

## Status

Aceita em 18 de julho de 2026.

## Contexto

O lockfile do front-end referenciava um registro privado inacessível fora do ambiente de criação. Além disso, portas comuns do host já podiam estar ocupadas por outros projetos.

## Decisão

Manter URLs do lockfile no registro público do npm, instalar com `npm ci` nas imagens e permitir que todas as portas publicadas pelo Compose sejam substituídas via `.env`. A rede interna dos containers continua usando as portas padrão dos serviços.

## Consequências

- Builds deixam de depender de infraestrutura privada.
- Instalações respeitam exatamente o lockfile versionado.
- Projetos locais podem coexistir sem desligar serviços alheios.
- A documentação conserva portas padrão simples para novos usuários.
