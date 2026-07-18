# AGENTS.md — Instruções obrigatórias para o Codex

## Missão

Construir o Nexus d20 como produto web comercializável, simples para jogadores iniciantes e poderoso para mestres, sem desviar do escopo fechado do MVP.

## Regra principal

Antes de alterar código:

1. Leia `docs/PRODUCT_SPEC.md`.
2. Leia `docs/RULES_ENGINE.md`.
3. Leia `docs/PERMISSIONS.md`.
4. Leia `DECISIONS.md`.
5. Identifique a fase correspondente no `ROADMAP.md`.

Não invente novas regras de negócio. Quando houver ambiguidade, implemente a alternativa mais conservadora e registre a decisão em `docs/adr/`.

## Escopo congelado

O escopo do MVP está congelado. Novas funcionalidades não devem ser adicionadas durante a execução, exceto:

- correções de segurança;
- correções de regra;
- correções de acessibilidade;
- correções necessárias para concluir um requisito já documentado.

Ideias adicionais devem ser registradas em `docs/V2_NOTES.md`, sem serem implementadas no MVP.

## Princípios técnicos

- O motor de regras deve ser puro, determinístico e coberto por testes.
- A interface nunca deve recalcular regras importantes por conta própria.
- A API é a fonte da verdade para regras e permissões.
- Use `Decimal` para moedas, pesos e percentuais persistidos.
- Use UTC no banco; exiba datas no fuso do usuário.
- Peso é exibido em quilogramas.
- Distância de combate é exibida em metros.
- Distância de viagem é exibida em quilômetros.
- Não misture regras de D&D 2024.
- Não use IA para definir quantidade de slots, progressão, dano ou efeitos oficiais.
- Toda alteração mecânica do mestre deve gerar auditoria reversível.
- Notas dos jogadores possuem proteção especial e não podem ser editadas pelo mestre.

## Segurança e multi-tenant

- Todo acesso deve ser limitado por `campaign_id` e participação na campanha.
- Nunca confie em IDs enviados pelo front-end sem verificar autorização.
- O mestre pode editar campos de ficha da campanha, exceto notas pertencentes aos usuários.
- Notas privadas não podem ser lidas pelo mestre.
- Anexos devem usar URLs assinadas; não exponha buckets publicamente.
- Segredos nunca devem ser versionados.

## Banco e migrações

- Toda alteração de schema exige migração Alembic.
- Migrações devem ser reversíveis quando possível.
- Não remova colunas em uma mesma versão em que deixou de usá-las; faça migração em duas etapas.
- Modelos-base e instâncias devem permanecer separados.

## Padrões de API

- Rotas versionadas em `/api/v1`.
- Use schemas distintos para entrada e saída.
- Erros devem ter código estável e mensagem em português.
- Use idempotência em descanso, transferências e ações que possam ser repetidas.
- Operações de simulação não alteram estado.
- Operações de aplicação exigem confirmação explícita e registram auditoria.

## Padrões de front-end

- Mobile-first e responsivo.
- Interface em português do Brasil.
- Não ocultar regras importantes apenas por cor.
- Componentes devem suportar teclado e leitores de tela.
- Informações secretas do mestre nunca devem chegar ao cliente do jogador.
- O gráfico de atributos deve ser SVG acessível com alternativa textual.

## Testes obrigatórios

Antes de concluir uma tarefa:

- testes unitários do motor de regras;
- teste de autorização relevante;
- teste de endpoint quando houver API;
- lint e typecheck do front-end;
- migration check quando houver schema.

Cobertura prioritária:

- ataque e desgaste;
- itens mágicos e limite de 50%;
- redução do dado de dano;
- visibilidade por profissão;
- carga e deslocamento;
- fadiga oculta;
- descanso longo;
- proteção de notas;
- edição do mestre e auditoria.

## Git

- Branches: `feat/`, `fix/`, `chore/`, `docs/`.
- Commits pequenos e objetivos.
- Não misture refatoração sem relação com a tarefa.
- PR deve informar alterações, impacto, testes e migrações.

## Definição de pronto

Uma tarefa só está pronta quando:

- requisito implementado;
- testes passando;
- documentação atualizada;
- estados de erro tratados;
- autorização aplicada;
- auditoria aplicada quando necessária;
- nenhuma regra de 2024 foi introduzida;
- nenhuma nota privada foi exposta.
