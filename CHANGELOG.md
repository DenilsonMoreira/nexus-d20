# Changelog

## 0.1.0 — 2026-07-18

- Fundação Docker do monorepo.
- Especificação fechada do MVP.
- Motor inicial de ataque, durabilidade, carga e descanso.
- Mockup funcional responsivo.
- Migração inicial de usuários, campanhas, membros, notas e auditoria.
- CI, Dependabot e templates do GitHub.
- Stack completa validada com health checks saudáveis.
- Lockfile público e instalação front-end determinística com `npm ci`.
- Portas locais do Compose configuráveis por ambiente.
- Migração inicial alinhada aos modelos e aprovada pelo `alembic check`.
- Cadastro, login, refresh rotativo e logout com cookies HTTP-only.
- Senhas Argon2 e tokens de atualização armazenados somente como hash.
- Erros de autenticação com códigos estáveis e mensagens em português.
- Campanhas isoladas por participação e `campaign_id` no back-end.
- Convites expiráveis vinculados ao e-mail, com token persistido apenas como hash.
- Papéis de mestre, jogador e observador, com proteção do proprietário.
- Arquivamento de campanha em vez de exclusão destrutiva.
- Serviço transacional reutilizável de auditoria com antes/depois.
- Metadados de reversibilidade, responsável, horário e motivo.
- Reversão segura de arquivamento de campanha com proteção contra repetição e estado divergente.
- Recuperação de acesso por e-mail com resposta anti-enumeração.
- Tokens de redefinição de uso único armazenados somente como hash.
- Revogação de sessões e JWTs após troca de senha.
- Mailpit versionado para inspeção de e-mails no desenvolvimento.
- Fase 2 iniciada com ficha básica persistida, validada e auditada.
- Endpoints multi-tenant para criação, listagem, leitura e atualização de personagens.
- Painel responsivo conectado à API, com composição desktop e navegação móvel gótica.
- Editor responsivo para identidade, combate, movimento e os seis atributos da ficha.
- Reversão segura de edições de ficha feitas pelo mestre, com detecção de mudanças posteriores.
- Proficiências categorizadas e recursos de classe persistidos como coleções da ficha.
- Editor e painel responsivos para proficiências, valores atuais, máximos e gatilhos de recuperação.
- Fase 2 concluída com ficha persistida, editável, auditada e protegida por campanha.
- Fase 3 iniciada com tabela determinística de XP e bônus de proficiência do SRD 5.1.
- Simulação pura do próximo nível, com elegibilidade por XP, suporte a avanço por marco e limite no nível 20.
- Fundação de progressão das doze classes SRD com dados de vida, ganho de PV e escolhas pendentes de aumento de atributo.
