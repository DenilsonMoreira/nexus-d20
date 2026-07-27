# ADR 0013 — Simulação de aumento de atributos

## Status

Aceita em 27 de julho de 2026.

## Contexto

A fundação de progressão por classe já identifica os níveis que concedem aumento de atributos, mas ainda não representa a escolha nem seus efeitos derivados. Alterar Constituição também afeta retroativamente o máximo de PV de todos os níveis alcançados.

## Decisão

Criar uma simulação pura que aceita exatamente uma das distribuições previstas pelas regras de 2014:

- `+2` em um atributo; ou
- `+1` em dois atributos diferentes.

Nenhum aumento pode elevar a pontuação acima de 20. A resposta apresenta pontuações e modificadores antes/depois. A diferença do modificador de Constituição é multiplicada pelo nível total resultante para informar o ajuste necessário no máximo de PV.

Essa rota não determina se a classe concede aumento naquele nível. O assistente completo será responsável por compor a concessão da classe com esta escolha. Talentos, aplicação e persistência permanecem fora deste recorte.

## Consequências

- Distribuições inválidas são rejeitadas antes de qualquer alteração.
- O cliente não precisa recalcular modificadores ou efeitos retroativos de Constituição.
- A simulação continua reutilizável para personagens de uma ou várias classes.
- A aplicação futura poderá auditar pontuações e PV usando o mesmo resultado determinístico.
