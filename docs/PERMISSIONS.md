# Permissões e privacidade

## Papéis

### Mestre

Pode administrar campanha, regras, fichas, itens, encontros, condições e painéis. Não possui poder de escrita sobre notas de jogadores e não lê notas privadas.

### Jogador

Administra seus personagens conforme regras da campanha, seus inventários permitidos e suas próprias notas.

### Observador

Visualiza apenas conteúdo compartilhado.

## Matriz resumida

| Recurso | Mestre | Autor jogador | Outro jogador |
|---|---|---|---|
| Campo mecânico da ficha | Ler/editar | Ler/editar conforme regra | Não |
| Nota privada | Não | Ler/editar/excluir | Não |
| Nota compartilhada | Ler, sem editar | Ler/editar/excluir | Ler |
| Visibilidade da nota | Não altera | Altera | Não |
| Item do personagem | Ler/editar/auditar | Usar/equipar | Não |
| Regra da campanha | Administrar | Ler | Ler |
| Segredo do mestre | Administrar | Não | Não |

## Regras técnicas

- `owner_user_id` de nota é imutável.
- Updates e deletes de nota exigem o proprietário.
- Compartilhamento não transfere autoria.
- Mestre pode criar anotação própria relacionada, nunca alterar a nota original.
- Endpoints de jogador retornam DTOs sem campos secretos.
- Campos secretos não devem ser enviados e ocultados via CSS.
- Toda edição do mestre em ficha gera auditoria.
- Auditoria de nota privada não aparece ao mestre.

## Cenários de teste obrigatórios

1. Mestre tenta ler nota privada: 404 ou 403 sem revelar existência detalhada.
2. Mestre tenta editar nota compartilhada: 403.
3. Jogador de outra campanha tenta enumerar personagem: 404.
4. Mestre altera PV: sucesso e audit log.
5. Observador tenta aplicar condição: 403.
6. Tela pública não contém segredo no payload.
