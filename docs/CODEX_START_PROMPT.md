# Prompt inicial recomendado para o Codex

Use o texto abaixo ao iniciar a implementação da primeira fase:

```text
Trabalhe no repositório Nexus d20.

Leia integralmente AGENTS.md, ROADMAP.md, DECISIONS.md e os documentos em docs/ antes de alterar arquivos. Implemente somente a próxima fase incompleta do ROADMAP, começando pela Fase 1. Não adicione funcionalidades de V2 e não misture regras de D&D 2024.

Primeiro, faça uma auditoria do estado atual e crie um plano curto com os arquivos que serão alterados. Depois implemente a fatia vertical completa, incluindo migrações, autorização multi-tenant, testes, documentação e tratamento de erros.

Requisitos invariáveis:
- motor de regras determinístico;
- unidades em kg, m e km;
- toda edição mecânica do mestre gera auditoria;
- mestre não pode ler notas privadas nem editar notas de jogadores;
- simulações não alteram estado;
- nenhuma informação secreta pode ser enviada ao cliente do jogador.

Ao terminar, execute os checks disponíveis, informe os resultados e abra um PR pequeno e revisável.
```
