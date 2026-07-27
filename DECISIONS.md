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

Eventos de auditoria são gravados na mesma transação da alteração de domínio e registram entidade, ação, responsável, antes, depois e motivo quando aplicável. Apenas eventos explicitamente marcados como reversíveis podem ser desfeitos. A reversão exige mestre, motivo, compatibilidade com o estado atual e cria um novo evento ligado ao original; o histórico nunca é apagado. Arquivamento de campanha e edições de ficha feitas pelo mestre possuem reversão automática com verificação integral do estado posterior.

## D-027 — Recuperação de acesso

Recuperação de senha usa token opaco de uso único, com validade de 30 minutos e persistência somente do SHA-256. A solicitação sempre retorna a mesma resposta, exista ou não a conta. Ao redefinir a senha, todas as sessões são revogadas e a versão de autenticação do usuário é incrementada, invalidando também JWTs já emitidos. Desenvolvimento usa Mailpit oficial com versão fixa; produção exige SMTP configurado por ambiente.

## D-028 — Propriedade e visibilidade da ficha

Cada personagem pertence a uma campanha e possui um usuário responsável que deve ser mestre ou jogador participante. O mestre enxerga e edita todas as fichas da campanha; o jogador enxerga e edita somente as próprias; observadores e outros jogadores não recebem a ficha no payload. Tentativas de acesso direto sem permissão retornam 404. Criação e alterações mecânicas geram auditoria transacional com antes e depois; edições feitas pelo mestre são reversíveis enquanto a ficha ainda corresponder ao estado posterior auditado. Modificadores de atributo são calculados pela API segundo a regra de 2014.

## D-029 — Proficiências e recursos declarativos

Proficiências da ficha são registros declarativos categorizados como salvaguarda, perícia, idioma, ferramenta, arma, armadura ou outra; esta fase não infere bônus nem concede proficiências automaticamente. Recursos possuem nome, valor atual, máximo e gatilho informativo de recuperação por descanso curto, descanso longo ou ação manual. Quantidades e recuperação efetiva continuam sob responsabilidade do motor de progressão e descanso nas fases correspondentes. As coleções pertencem ao personagem, seguem as mesmas permissões e integram os snapshots reversíveis de auditoria.

## D-030 — Base determinística de progressão

Os limiares de experiência e o bônus de proficiência seguem a tabela de avanço do SRD 5.1 e usam o nível total do personagem. A simulação avalia somente o próximo nível, nunca altera a ficha e mantém efeitos específicos de classe, pontos de vida, magias e multiclasse fora desta fundação. Quando pontos de experiência não são informados, a qualificação retorna `not_evaluated`, preservando campanhas que adotam avanço por marco sem presumir sua política.

## D-031 — Fundação da progressão por classe

A primeira camada de progressão por classe cobre as doze classes do SRD 5.1 apenas para dado de vida, valor fixo de PV, rolagem informada pelo usuário e níveis que concedem aumento de atributo. O motor nunca realiza uma rolagem aleatória e aplica ganho mínimo de 1 PV após o modificador de Constituição. A ausência do método de PV e os níveis de aumento de atributo são devolvidos como escolhas pendentes. O resultado não representa uma subida completa: características, subclasses, magias e multiclasse permanecem explicitamente fora deste recorte e devem ser compostos antes da aplicação persistente.

## D-032 — Simulação de aumento de atributos

O aumento de atributos de 2014 aceita exatamente `+2` em um atributo ou `+1` em dois atributos diferentes e não eleva uma pontuação acima de 20. A simulação devolve pontuações e modificadores antes/depois. Quando Constituição muda de faixa de modificador, o ajuste do máximo de PV é a diferença do modificador multiplicada pelo nível total resultante, contemplando retroativamente todos os níveis alcançados. Talentos e aplicação persistente não integram esta camada.
