# Privacidade e proteção de dados

## Escopo

O Nexus d20 trata dados cadastrais (nome de exibição e e-mail), conteúdo de
campanhas, personagens, notas, imagens, registros de segurança e auditoria.
Senhas são armazenadas somente como hash Argon2; tokens persistidos são
armazenados como hash.

## Finalidades

- autenticar e proteger a conta;
- executar as funcionalidades contratadas;
- manter integridade, prevenção a abuso e trilha de auditoria;
- atender suporte, portabilidade e exclusão.

Não há venda de dados pessoais. Um operador comercial deve preencher identidade,
contato do encarregado, bases legais, fornecedores e transferências internacionais
antes de disponibilizar o serviço ao público.

## Direitos do titular

O titular autenticado pode obter uma exportação em JSON por
`GET /api/v1/account/export` e solicitar exclusão por `DELETE /api/v1/account`
com `{"confirmation":"EXCLUIR"}`. A exclusão revoga sessões, elimina notas,
mídias e personagens do titular, arquiva campanhas próprias e pseudonimiza a
conta. Eventos mínimos de auditoria podem ser preservados por até 730 dias para
segurança e exercício regular de direitos.

## Retenção

- sessões expiradas ou revogadas: até 90 dias;
- tokens de recuperação expirados ou usados: até 90 dias;
- auditoria: 730 dias, com revisão antes de qualquer descarte;
- backups: 30 dias por padrão;
- dados ativos: enquanto a conta ou obrigação aplicável existir.

A rotina `python -m app.maintenance retention --apply` remove credenciais
temporárias vencidas. Eventos antigos de auditoria são apenas sinalizados para
revisão, evitando descarte automático de prova ou quebra de integridade.

## Incidentes

Preservar logs correlacionados por `X-Request-ID`, conter o acesso, avaliar
impacto, registrar decisões e cumprir os prazos legais de comunicação aplicáveis.
Nunca inserir senhas, tokens, corpos de notas ou conteúdo privado nos logs.
