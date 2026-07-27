# ADR 0014 — Catálogo público de subclasses SRD

## Status

Aceita em 27 de julho de 2026.

## Contexto

O assistente precisa saber quando uma classe exige subclasse e quais opções podem aparecer publicamente. Algumas descrições de classe mencionam opções que não são detalhadas pelo SRD 5.1, enquanto o produto só pode distribuir conteúdo de fonte autorizada.

## Decisão

Incluir no catálogo público somente a subclasse detalhada pelo SRD 5.1 para cada classe:

- Caminho do Berserker, Colégio do Conhecimento, Domínio da Vida e Círculo da Terra;
- Campeão, Caminho da Mão Aberta, Juramento de Devoção e Caçador;
- Ladrão, Linhagem Dracônica, Patrono Corruptor e Escola de Evocação.

Cada definição registra classe, identificador estável, rótulo, nível de escolha e origem `srd_5_1`. A simulação valida o nível e a associação entre classe e subclasse. Nenhuma opção é selecionada automaticamente.

Opções apenas mencionadas, mas não detalhadas pelo SRD, ficam fora do catálogo público. Conteúdo privado ou personalizado será modelado separadamente.

## Consequências

- O catálogo público possui origem auditável e escopo de licença conservador.
- Escolhas de 1º nível também podem ser validadas durante criação ou importação.
- A interface sempre exige confirmação explícita do usuário.
- Novas fontes autorizadas ou conteúdo privado não alteram as definições SRD existentes.
