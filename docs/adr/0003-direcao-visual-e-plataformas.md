# ADR 0003 — Direção visual e plataformas

## Status

Aceita em 18 de julho de 2026.

## Contexto

O produto possui um mockup gótico com versões desktop e mobile. Era necessário definir se ele representava apenas inspiração ou uma direção visual permanente, além de ordenar o desenvolvimento web e nativo.

## Decisão

Adotar `docs/images/nexus-d20-mockup.png` como referência visual canônica. Construir primeiro a aplicação web mobile-first e responsiva, adaptando conteúdo e navegação por contexto. Planejar um aplicativo Android nativo somente após a primeira versão web, fora do MVP.

## Consequências

- O sistema visual deve preservar a atmosfera gótica escura e dourada do mockup.
- Acessibilidade, legibilidade e desempenho prevalecem sobre ornamentos.
- Desktop e mobile compartilham linguagem visual, mas não uma composição rígida.
- O MVP não recebe dependências específicas de Android.
