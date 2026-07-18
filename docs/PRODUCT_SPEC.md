# Especificação do produto — Nexus d20

## Problema

Jogadores e mestres usam várias ferramentas para ficha, magias, evolução, notas, inventário e campanha. O Nexus d20 centraliza essas informações e automatiza regras repetitivas sem retirar a decisão final do mestre.

## Público

- Jogadores de D&D 5e 2014 que querem uma ficha mais orientada.
- Mestres que precisam organizar campanhas, regras, criaturas e consequências.
- Grupos que usam regras homebrew e desejam histórico auditável.

## Experiência do jogador

### Ficha

- Identidade, retrato, classe, subclasse, nível, antecedente e alinhamento.
- PV, PV temporários, CA, iniciativa, deslocamento e condições.
- Atributos: Força, Destreza, Constituição, Inteligência, Sabedoria e Carisma.
- Pontuação e modificador textual.
- Gráfico hexagonal acessível.
- Recursos de classe e descanso.

### Evolução

- Simulação de nível.
- Resumo antes/depois.
- Escolhas obrigatórias.
- Validação de multiclasse.
- Histórico e reversão.

### Magias

- Conhecidas, preparadas, grimório, truques, pacto, racial e itens.
- Slots e recuperação.
- Filtros por nível, escola, concentração, ritual e efeito.
- Descrição permitida pelo conteúdo disponível.

### Inventário

- Peso em kg, recipiente e localização.
- Arma ativa e cálculo de ataque.
- Material, qualidade, durabilidade e estado.
- Visibilidade da porcentagem conforme profissão.
- Notas e imagens vinculadas.

### Ataque

O jogador escolhe arma e alvo, informa o valor natural do d20 e recebe:

- modificador de ataque detalhado;
- total;
- acerto, erro ou crítico;
- desgaste calculado;
- alteração de durabilidade;
- risco de quebra;
- histórico.

## Experiência do mestre

### Grupo ativo

Cards selecionáveis com:

- PV, CA, movimento, recursos e condições;
- slots;
- arma ativa, ataque, dano e durabilidade;
- carga e risco de fadiga;
- atalhos para ficha, condição e descanso.

### Descanso longo

- Simulação sem mutação.
- PV, slots, recursos, dados de vida, exaustão e fadiga.
- Itens mágicos se autorreparam.
- Cargas são restauradas conforme gatilho.
- Alimento, água, antimagia e interrupções são considerados.
- Aplicação idempotente, auditável e reversível.

### Biblioteca

- Modelos e instâncias de itens.
- Magias, condições, preços, serviços e lojas.
- Copiar e personalizar sem alterar original.
- Informação secreta e identificação parcial.

### Bestiário

- Criaturas, ações, magia, equipamento, saque e comportamento.
- Cópias e modelos como elite, chefe, ferido ou corrompido.
- Biomas e tabelas ponderadas.

### Encontros

- Bioma, nível, quantidade, estado atual do grupo, clima, horário e perigo.
- Combate, social, exploração ou evento.
- Dificuldade é estimativa.
- Persistência de criaturas que escapam.

### Segundo cérebro

- Nós: NPC, local, facção, item, pista, evento, segredo, missão e sessão.
- Arestas tipadas.
- Conhecimento por personagem e informação falsa.
- Linha do tempo e consequências futuras.

### Construtor de painéis

- Cards arrastáveis e redimensionáveis.
- Layouts para combate, exploração, cidade, loja, descanso e investigação.
- Modo apresentação com filtragem de segredos.

## Requisitos não funcionais

- Mobile-first.
- Tempo de resposta percebido abaixo de 300 ms para operações locais comuns.
- Auditoria de alterações mecânicas.
- Exportação futura de dados.
- Backups e recuperação.
- Acessibilidade WCAG 2.2 AA como objetivo.
- Privacidade por padrão.

## Fora do MVP

- VTT completo com mapa tático avançado.
- Marketplace público.
- Conteúdo integral de livros não SRD.
- Aplicativo nativo.
- Geração automática de aventuras por IA.
- Voz e vídeo.
