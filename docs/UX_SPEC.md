# Especificação de UX

## Identidade visual

Tema escuro de fantasia, com contraste alto, superfícies discretas e acentos dourados. O produto deve parecer ferramenta profissional, não uma ficha decorativa ilegível.

O arquivo `docs/images/nexus-d20-mockup.png` é a referência visual canônica. Preservar:

- fundo preto e grafite com variações sutis de profundidade;
- dourado envelhecido nos contornos, ícones, títulos e ações primárias;
- tipografia de fantasia nos títulos, combinada com tipografia altamente legível nos dados;
- cards com bordas finas, cantos discretos e alta densidade organizada;
- iconografia coerente com fantasia medieval, sem comprometer reconhecimento;
- atmosfera gótica sem texturas ou ornamentos que prejudiquem leitura e desempenho.

O mockup orienta o sistema visual, não dimensões rígidas. Contraste, foco visível, ampliação de texto e preferências de movimento devem continuar compatíveis com WCAG 2.2 AA.

## Web responsivo

- Implementar mobile-first com aprimoramento progressivo para tablet e desktop.
- Reorganizar conteúdo por prioridade de uso; não comprimir o painel desktop inteiro no celular.
- Usar navegação inferior no celular para destinos frequentes e navegação lateral em telas amplas.
- Manter alvos de toque com pelo menos 44 × 44 px.
- Evitar rolagem horizontal em fluxos comuns; tabelas complexas devem oferecer representação em cards.
- Preservar dados e ações essenciais quando cards mudarem de coluna ou forem recolhidos.
- Validar, no mínimo, larguras de 360, 768, 1024 e 1440 px.

## Navegação do jogador

- Ficha
- Evolução
- Magias
- Inventário
- Durabilidade
- Notas
- Campanha

## Navegação do mestre

- Visão geral
- Grupo ativo
- Biblioteca
- Bestiário
- Encontros
- Teia
- Linha do tempo
- Painéis
- Configurações

## Gráfico de atributos

Ordem dos eixos:

- Carisma
- Inteligência
- Sabedoria
- Força
- Destreza
- Constituição

Mostrar pontuação e modificador. Incluir lista textual para acessibilidade.

## Durabilidade

Jogador sem profissão vê estado. Com profissão vê pontos, percentual e histórico permitido. Mestre sempre vê detalhes.

## Ações perigosas

- Simular antes.
- Mostrar antes/depois.
- Solicitar motivo quando o mestre ultrapassa proteção mágica ou altera regra.
- Permitir desfazer quando seguro.

## Mobile

Priorizar durante a sessão:

- PV e CA;
- recursos;
- ataque rápido;
- slots;
- arma ativa;
- estado de equipamento;
- notas rápidas.

O navegador móvel é a experiência mobile da primeira versão. O aplicativo Android nativo não faz parte do MVP e não deve introduzir dependências ou decisões prematuras na arquitetura web.
