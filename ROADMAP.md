# ROADMAP — Nexus d20

## Estratégia

O produto será construído em fatias verticais. Cada fase deve produzir algo utilizável e testável. Não iniciar uma fase sem concluir os critérios de aceite da anterior.

## Fase 0 — Fundação do repositório

**Status:** concluída em 18 de julho de 2026.

- Monorepo, Docker Compose e variáveis de ambiente.
- API FastAPI e front-end Next.js executáveis.
- PostgreSQL, Redis e MinIO.
- CI, lint, testes e migrações.
- Documentação de regras, segurança e produto.

**Aceite:** `docker compose up --build` inicia todos os serviços e os health checks ficam saudáveis.

## Fase 1 — Identidade, campanhas e permissões

**Status:** concluída em 22 de julho de 2026.

- Cadastro, login, refresh token e recuperação de acesso.
- Criação de campanha.
- Convites e papéis: mestre, jogador e observador.
- Middleware de autorização multi-tenant.
- Auditoria básica.

**Aceite:** usuário só acessa campanhas das quais participa; testes provam a proteção.

## Fase 2 — Ficha inteligente

**Status:** em andamento desde 23 de julho de 2026.

- Personagem, atributos, modificadores e gráfico hexagonal.
- Classe, nível, PV, CA, deslocamento, proficiências e recursos.
- Ficha responsiva.
- Edição pelo jogador e pelo mestre conforme permissões.

**Aceite:** ficha completa persistida e auditada.

## Fase 3 — Progressão e magias

- Motor de progressão D&D 5e 2014.
- Assistente de subida de nível.
- Conhecidas, preparadas, grimório, truques e slots.
- Multiclasse com validação.
- Simulação antes de confirmar.

**Aceite:** progressão testada classe a classe para conteúdo SRD incluído.

## Fase 4 — Inventário, materiais e durabilidade

- Catálogo, modelos, variações e instâncias.
- Materiais, qualidade, peso, preço e durabilidade.
- Ataques e cálculo de desgaste.
- Penalidades e risco de quebra.
- Visibilidade por profissão.
- Itens mágicos, limite de 50% e autorreparo.

**Aceite:** cenários de ferro, aço, crítico, falha crítica e reparo cobertos por testes.

## Fase 5 — Notas e mídia

- Notas privadas e compartilhadas.
- Imagens em MinIO/S3.
- Vínculos com personagem, local, item, NPC, sessão e evento.
- Política que impede edição pelo mestre.

**Aceite:** teste de segurança prova que o mestre não lê nota privada nem edita qualquer nota de jogador.

## Fase 6 — Painel do mestre e descanso

- Grupo ativo e personagens selecionados.
- Armas ativas e recursos atuais.
- Simulação e aplicação do descanso longo.
- Reversão e auditoria.
- Condições e exaustão.

**Aceite:** descanso restaura apenas recursos elegíveis e respeita alimento, água e antimagia.

## Fase 7 — Biblioteca do mestre

- Itens, magias, condições, preços e serviços.
- Duplicação e personalização.
- Lojas e estoque.
- Conteúdo secreto e identificado.

**Aceite:** copiar nunca altera o original; instâncias são independentes.

## Fase 8 — Bestiário e encontros

- Criaturas, cópias, equipamentos e tesouro.
- Biomas, clima, horário e perigo.
- Gerador ponderado de encontros.
- Início de combate e histórico.

**Aceite:** dificuldade é apresentada como estimativa e pode ser ajustada pelo mestre.

## Fase 9 — Viagem, peso e fadiga

- Peso em kg e distâncias métricas.
- Sobrecarga variante.
- Planejamento de viagem.
- Marcha forçada oficial.
- Fadiga oculta opcional.
- Comida, água, montarias e veículos.

**Aceite:** inventário recalcula carga e viagem recalcula deslocamento e risco individual.

## Fase 10 — Teia de conhecimento e construtor de painéis

- Nós, conexões, linha do tempo e segredos.
- Cards configuráveis e layouts.
- Modo apresentação sem dados privados.
- Modelos de combate, cidade, loja, exploração e descanso.

**Aceite:** dados secretos não são serializados para telas públicas.

## Fase 11 — Preparação comercial

- Observabilidade, backups e restauração.
- Rate limit, política de retenção e exportação de dados.
- Termos, privacidade e exclusão de conta.
- Testes de carga e segurança.
- Deploy de homologação.

**Aceite:** checklist de produção completo em `docs/DEPLOYMENT.md`.

## V2

Consulte `docs/V2_NOTES.md`. Não implementar itens de V2 durante o MVP.
