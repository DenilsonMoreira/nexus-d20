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
   - cadastro, login, refresh, logout, recuperação de acesso e hash Argon2;
   - cookies HTTP-only;
   - testes de sessão.

2. **Campanhas e convites** — concluído
   - CRUD, papéis e convites;
   - middleware de membro;
   - isolamento multi-tenant.

3. **Auditoria reutilizável** — concluído
   - serviço transacional;
   - antes/depois;
   - motivo e reversão.

4. **Ficha básica** — concluído
   - [x] personagem, atributos, modificadores, PV, CA e movimento;
   - [x] gráfico responsivo conectado à API;
   - [x] edição completa da ficha na interface;
   - [x] proficiências e recursos.

5. **Progressão e magias** — em andamento
   - [x] tabela de XP e bônus de proficiência do SRD 5.1;
   - [x] simulação pura do próximo nível;
   - [ ] progressão e escolhas por classe;
     - [x] dados de vida, PV e níveis de aumento de atributo das doze classes SRD;
     - [x] escolha de aumento de atributos e ajuste retroativo de PV por Constituição;
     - [x] catálogo SRD e pontos obrigatórios de escolha de subclasse;
     - [ ] características, subclasses e demais escolhas de cada nível;
   - [ ] aplicação idempotente e auditada;
   - [ ] magias, slots e multiclasse.

6. **Profissões e visibilidade**
   - domínios artesanais;
   - política de durabilidade detalhada.

7. **Catálogo de materiais e itens**
   - templates, versões, cópias e instâncias;
   - seed próprio sem conteúdo proibido.

8. **Ataques persistidos**
   - seleção de alvo e arma;
   - evento de desgaste;
   - aplicação e auditoria.

9. **Notas protegidas**
   - CRUD do autor;
   - compartilhamento;
   - testes negativos para mestre.

10. **Armazenamento de imagens**
   - upload validado;
   - URL assinada;
   - remoção segura.

11. **Descanso de grupo**
    - simulação e aplicação idempotente;
    - itens mágicos, slots, PV, recursos e condições.

Consulte `ROADMAP.md` para as fases posteriores.
