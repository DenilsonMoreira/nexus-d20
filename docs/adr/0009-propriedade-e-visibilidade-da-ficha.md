# ADR 0009 — Propriedade e visibilidade da ficha

## Contexto

A especificação permite que o mestre edite fichas da campanha e que o jogador administre os próprios personagens, mas não define compartilhamento de fichas entre jogadores ou observadores.

## Decisão

Cada personagem pertence a uma campanha e a um usuário responsável, obrigatoriamente mestre ou jogador participante. Mestres acessam todas as fichas da campanha. Jogadores acessam somente as próprias. Outros jogadores e observadores não recebem dados da ficha e recebem 404 no acesso direto.

Criação e atualização são auditadas na mesma transação, com estado anterior e posterior. A API calcula os modificadores a partir das seis pontuações usando `floor((pontuação - 10) / 2)`.

## Consequências

- Conhecer o UUID de um personagem não revela sua existência.
- Uma política futura de ficha compartilhada exigirá decisão e campo explícitos; não será inferida da participação na campanha.
- O frontend consome valores e modificadores calculados pela API e mantém alternativa textual para o gráfico.
