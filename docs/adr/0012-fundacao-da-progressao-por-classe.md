# ADR 0012 — Fundação da progressão por classe

## Status

Aceita em 26 de julho de 2026.

## Contexto

O assistente de subida de nível precisa compor várias regras independentes. Implementar de uma vez PV, todas as características, subclasses, magias, multiclasse e persistência aumentaria o risco de misturar conteúdo incompleto com uma operação mecânica definitiva.

## Decisão

Criar uma camada pura para as doze classes do SRD 5.1 que simula apenas:

- dado de vida e valor fixo de PV;
- resultado de uma rolagem de dado informada pelo usuário;
- ganho mínimo de 1 PV após o modificador de Constituição;
- níveis em que existe uma escolha de aumento de atributo.

O motor não gera números aleatórios. Quando o método de PV não foi escolhido, devolve uma escolha pendente. Nos níveis de aumento de atributo, também devolve uma escolha pendente, sem alterar pontuações.

Características, subclasses, magias e multiclasse não fazem parte desta resposta. Nenhuma aplicação persistente será criada enquanto a simulação completa não puder compor todas essas camadas.

## Consequências

- O cálculo de PV pode ser testado igualmente para todas as classes.
- A interface pode orientar escolhas sem falsamente confirmar uma subida completa.
- Rolagens permanecem explícitas e reproduzíveis.
- As próximas camadas podem adicionar características e magias sem reimplementar a base de PV.
