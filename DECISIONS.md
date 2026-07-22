# DECISIONS — Decisões arquiteturais e de produto

## D-001 — Regras-base

A aplicação usa exclusivamente D&D 5e de 2014 como padrão. Regras de 2024 não são misturadas automaticamente.

## D-002 — Conteúdo público

Somente conteúdo autorizado do SRD 5.1 pode ser incluído publicamente. Conteúdo privado pode ser cadastrado pelo usuário sob sua responsabilidade.

## D-003 — Regras personalizadas

O mestre pode criar versões e substituições de regras. Alterações possuem origem, versão, vigência e histórico. Mudanças não alteram retroativamente eventos antigos.

## D-004 — Motor determinístico

Cálculos mecânicos são executados por código testável. IA futura apenas explica, resume ou sugere.

## D-005 — Sistema métrico

Peso em kg; combate e alcance em metros; viagem em quilômetros. Conversões exatas são internas.

## D-006 — Durabilidade em pontos

Durabilidade usa pontos máximos e atuais. Percentual é derivado. Materiais e qualidade definem o máximo.

## D-007 — Ataque e desgaste

- Total do ataque = d20 natural + modificador de ataque.
- Margem = valor absoluto do total − CA.
- Ataque comum: arma perde a margem em pontos.
- Falha crítica natural 1: margem × 2 na arma do atacante.
- Acerto crítico natural 20: arma atacante não desgasta; mestre pode aplicar margem × 2 ao equipamento do alvo.

## D-008 — Estados de item

- 76–100%: Ótimo.
- 51–75%: Bom.
- 26–50%: Regular.
- 11–25%: Ruim.
- 0–10%: Inutilizável.

A redução de dado começa abaixo de 50%, não em 50% exatos.

## D-009 — Itens mágicos

Itens mágicos possuem multiplicador de durabilidade, autorreparo e piso automático de 50%. Somente ação explícita do mestre permite ultrapassar o piso.

## D-010 — Visibilidade da durabilidade

O mestre vê pontos e percentual. O jogador só vê percentual quando possui profissão compatível com o domínio de fabricação do item; caso contrário vê apenas o estado.

## D-011 — Autoridade do mestre

O mestre pode editar informações mecânicas e compartilhadas das fichas da campanha. Toda alteração gera auditoria.

## D-012 — Proteção de notas

O mestre não pode editar ou excluir notas criadas pelos jogadores. Notas privadas não podem ser lidas pelo mestre. Essa proteção existe no back-end, não apenas na interface.

## D-013 — Catálogo e instâncias

Modelos, variações e instâncias são entidades diferentes. Copiar um item, magia, condição ou criatura nunca altera o original.

## D-014 — Teia de conhecimento

A primeira versão usa PostgreSQL com nós e arestas. Banco de grafos só será considerado se métricas demonstrarem necessidade.

## D-015 — Arquitetura

Monorepo com Next.js, FastAPI, PostgreSQL, MinIO e Redis, empacotado por Docker Compose.

## D-016 — Fadiga oculta

Fadiga oculta é homebrew opcional, separada da exaustão oficial e da marcha forçada. Pontuação exata pode ficar visível apenas ao mestre.

## D-017 — Simulação antes de mutação

Subida de nível, descanso, alterações de regras em massa e mudanças destrutivas devem oferecer simulação antes da aplicação.

## D-018 — Auditoria e reversão

Ações administrativas e mecânicas importantes geram registros com antes/depois, responsável, motivo e operação de reversão quando segura.

## D-019 — Licenciamento do código

Até definição comercial, o código usa licença proprietária. Não publicar com licença permissiva por acidente.

## D-020 — Imagens de infraestrutura reproduzíveis

Serviços de infraestrutura usam imagens oficiais com versões fixas e existentes no registro público. O MinIO usa `minio/minio:RELEASE.2025-09-07T16-13-09Z`; mudanças de versão exigem validação do Compose de desenvolvimento e produção.

## D-021 — Direção visual e plataformas

O mockup em `docs/images/nexus-d20-mockup.png` é a referência visual do produto: fantasia gótica escura, superfícies em preto e grafite, detalhes dourados e hierarquia tipográfica inspirada em livros de RPG. A implementação inicial é uma aplicação web mobile-first e responsiva. O layout deve adaptar hierarquia, navegação e densidade a cada viewport, sem apenas reduzir a composição desktop. Um aplicativo Android nativo será considerado após a primeira versão web e permanece fora do MVP.

## D-022 — Dependências front-end reproduzíveis

O lockfile do front-end deve referenciar somente o registro público `https://registry.npmjs.org/`, sem URLs de proxies ou registros internos de ambientes de desenvolvimento. Imagens Docker instalam dependências com `npm ci` para respeitar integralmente o lockfile.

## D-023 — Portas locais configuráveis

As portas publicadas pelo Compose de desenvolvimento possuem valores padrão documentados e podem ser substituídas por variáveis no `.env`. Endereços e portas internos entre containers permanecem fixos; a configuração serve apenas para evitar conflitos no host sem alterar a topologia da aplicação.

## D-024 — Sessões e credenciais

Senhas usam Argon2 e nunca são armazenadas ou registradas em texto puro. Tokens de acesso são JWTs curtos em cookie HTTP-only. Tokens de atualização são opacos, persistidos apenas como SHA-256, rotacionados a cada uso e revogáveis. Cookies usam `SameSite=Lax` e passam a `Secure` em produção.

## D-025 — Isolamento de campanhas e convites

Toda rota de campanha resolve o usuário autenticado e sua participação no banco; conhecer um `campaign_id` nunca concede acesso. Não membros recebem 404 para reduzir enumeração, enquanto membros sem papel suficiente recebem 403. Convites são opacos, persistidos apenas como SHA-256, expiram em sete dias e só podem ser aceitos pelo e-mail destinatário. O proprietário permanece mestre e não pode ser removido ou rebaixado. Exclusão de campanha arquiva o registro para permitir recuperação segura.

## D-026 — Auditoria transacional e reversão segura

Eventos de auditoria são gravados na mesma transação da alteração de domínio e registram entidade, ação, responsável, antes, depois e motivo quando aplicável. Apenas eventos explicitamente marcados como reversíveis podem ser desfeitos. A reversão exige mestre, motivo, compatibilidade com o estado atual e cria um novo evento ligado ao original; o histórico nunca é apagado. Inicialmente, somente o arquivamento de campanha possui reversão automática comprovadamente segura.
