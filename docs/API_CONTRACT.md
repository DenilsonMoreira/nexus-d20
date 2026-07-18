# Contrato inicial de API

Base: `/api/v1`

## Saúde

- `GET /health`

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
