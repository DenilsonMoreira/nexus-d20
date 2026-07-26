# ADR 0010 — Proficiências e recursos declarativos

## Contexto

A Fase 2 exige proficiências e recursos na ficha, enquanto concessão por classe, progressão e aplicação de descansos pertencem a fases posteriores. Antecipar essas regras misturaria persistência com mecânicas ainda não implementadas.

## Decisão

Proficiências são entradas explícitas com nome e uma das categorias: salvaguarda, perícia, idioma, ferramenta, arma, armadura ou outra. Não armazenamos bônus derivados nem concedemos entradas automaticamente.

Recursos são contadores explícitos com nome, valor atual, máximo e gatilho de recuperação por descanso curto, descanso longo ou ação manual. O gatilho é apenas declarativo nesta fase; não executa recuperação.

As duas coleções pertencem ao personagem, são substituídas integralmente quando enviadas na atualização e participam dos snapshots de auditoria e reversão.

## Consequências

- O backend não inventa progressão, quantidades ou bônus.
- Fases de progressão e descanso podem consumir os registros sem migrar dados genéricos da ficha.
- Duplicatas são rejeitadas e valores atuais não podem superar o máximo.
- A autorização continua centralizada no acesso ao personagem e à campanha.
