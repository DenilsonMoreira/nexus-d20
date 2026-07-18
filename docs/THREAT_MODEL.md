# Modelo de ameaças inicial

## Ativos

- notas privadas;
- segredos do mestre;
- fichas e histórico;
- imagens;
- tokens de sessão;
- conteúdo comercial futuro.

## Ameaças prioritárias

- IDOR entre campanhas;
- mestre excedendo permissão de notas;
- payload público com dados ocultos;
- upload malicioso;
- vazamento de URL de objeto;
- replay de descanso ou transferência;
- alteração concorrente de inventário;
- injeção em conteúdo personalizado;
- abuso de endpoints públicos.

## Controles

- autorização em serviço;
- DTOs específicos por papel;
- URLs assinadas;
- validação de MIME e tamanho;
- idempotência;
- optimistic locking;
- auditoria;
- rate limiting;
- CSP e sanitização.
