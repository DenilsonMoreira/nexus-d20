# Backlog de implementação para o Codex

Cada item deve resultar em PR independente ou em um conjunto pequeno e coerente.

## Fundação concluída neste pacote

- [x] Docker Compose de desenvolvimento e produção.
- [x] Next.js e FastAPI executáveis.
- [x] Banco, cache e objetos definidos.
- [x] Motor inicial de ataque, durabilidade, carga e descanso.
- [x] Migração de entidades centrais.
- [x] CI e documentação.

## Próximos PRs

1. **Autenticação e sessões** — concluído
   - cadastro, login, refresh, logout e hash Argon2;
   - cookies HTTP-only;
   - testes de sessão.

2. **Campanhas e convites** — concluído
   - CRUD, papéis e convites;
   - middleware de membro;
   - isolamento multi-tenant.

3. **Auditoria reutilizável**
   - serviço transacional;
   - antes/depois;
   - motivo e reversão.

4. **Ficha básica**
   - personagem, atributos, modificadores, PV, CA e movimento;
   - gráfico conectado à API.

5. **Profissões e visibilidade**
   - domínios artesanais;
   - política de durabilidade detalhada.

6. **Catálogo de materiais e itens**
   - templates, versões, cópias e instâncias;
   - seed próprio sem conteúdo proibido.

7. **Ataques persistidos**
   - seleção de alvo e arma;
   - evento de desgaste;
   - aplicação e auditoria.

8. **Notas protegidas**
   - CRUD do autor;
   - compartilhamento;
   - testes negativos para mestre.

9. **Armazenamento de imagens**
   - upload validado;
   - URL assinada;
   - remoção segura.

10. **Descanso de grupo**
    - simulação e aplicação idempotente;
    - itens mágicos, slots, PV, recursos e condições.

Consulte `ROADMAP.md` para as fases posteriores.
