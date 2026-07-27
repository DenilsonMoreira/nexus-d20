# Publicação no GitHub

## Criar o repositório

Crie um repositório privado chamado `nexus-d20` na conta desejada, sem adicionar README ou licença pela interface.

## Publicar

```bash
./scripts/publish-github.sh git@github.com:SEU_USUARIO/nexus-d20.git
```

Alternativa HTTPS:

```bash
./scripts/publish-github.sh https://github.com/SEU_USUARIO/nexus-d20.git
```

## Proteções recomendadas

- Branch padrão: `main`.
- Exigir PR.
- Exigir CI `backend` e `frontend`.
- Bloquear force-push.
- Exigir resolução de conversas.
- Ativar secret scanning e Dependabot.
