# Contrato inicial de API

Base: `/api/v1`

## Saúde

- `GET /health`

## Identidade

- `POST /auth/register` — cria usuário e sessão.
- `POST /auth/login` — autentica e cria sessão.
- `POST /auth/refresh` — rotaciona a sessão e emite novos cookies.
- `POST /auth/logout` — revoga a sessão atual e remove cookies.

Os tokens são enviados somente em cookies HTTP-only. O token de atualização é aceito apenas sob `/api/v1/auth` e cada uso invalida o token anterior.

## Campanhas

- `POST /campaigns` — cria campanha e torna o autor mestre proprietário.
- `GET /campaigns` — lista somente campanhas das quais o usuário participa.
- `GET /campaigns/{campaign_id}` — retorna campanha acessível ao membro.
- `PATCH /campaigns/{campaign_id}` — altera campanha; exige mestre.
- `DELETE /campaigns/{campaign_id}` — arquiva campanha; exige mestre.
- `POST /campaigns/{campaign_id}/invites` — cria convite de jogador ou observador.
- `POST /campaign-invites/{token}/accept` — aceita convite vinculado ao e-mail autenticado.
- `GET /campaigns/{campaign_id}/members` — lista participantes; exige mestre.
- `PATCH /campaigns/{campaign_id}/members/{user_id}` — altera jogador/observador.
- `DELETE /campaigns/{campaign_id}/members/{user_id}` — remove participante.

Não membros recebem `campaign_not_found` com HTTP 404, inclusive quando o UUID existe. O token bruto do convite é retornado somente no momento da criação ao mestre; o banco armazena apenas seu hash.

## Regras puras implementadas na fundação

- `POST /rules/attacks/resolve`
- `POST /rules/durability/preview`
- `POST /rules/encumbrance/calculate`
- `POST /rules/long-rest/simulate`

## Convenções

Resposta de erro:

```json
{
  "error": {
    "code": "stable_error_code",
    "message": "Mensagem legível em português",
    "details": {}
  }
}
```

Paginação futura:

```json
{
  "items": [],
  "next_cursor": null
}
```

## Idempotência

Rotas de aplicação de descanso, transferência e evolução usarão o cabeçalho:

```text
Idempotency-Key: uuid
```

## Simulação e aplicação

- `POST /.../simulate` nunca altera o banco.
- `POST /.../apply` recebe a simulação ou sua versão, valida mudanças concorrentes e grava auditoria.
