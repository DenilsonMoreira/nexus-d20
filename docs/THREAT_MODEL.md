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
- enumeração de contas pela recuperação de acesso.
- reutilização ou vazamento de token de recuperação.

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
- resposta uniforme para solicitação de recuperação;
- tokens opacos, curtos no tempo, armazenados como hash e de uso único;
- revogação de todas as sessões após troca de senha.
