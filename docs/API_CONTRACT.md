# Contrato inicial de API

Base: `/api/v1`

## Saúde

- `GET /health`

## Identidade

- `POST /auth/register` — cria usuário e sessão.
- `POST /auth/login` — autentica e cria sessão.
- `POST /auth/refresh` — rotaciona a sessão e emite novos cookies.
- `POST /auth/logout` — revoga a sessão atual e remove cookies.
- `POST /auth/password-reset/request` — solicita recuperação sem revelar se a conta existe.
- `POST /auth/password-reset/confirm` — redefine a senha com token de uso único.

Os tokens são enviados somente em cookies HTTP-only. O token de atualização é aceito apenas sob `/api/v1/auth` e cada uso invalida o token anterior.

Tokens de recuperação expiram em 30 minutos, são persistidos somente como hash e não podem ser reutilizados. A redefinição revoga todas as sessões e invalida tokens de acesso anteriores.

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

## Auditoria

- `GET /campaigns/{campaign_id}/audit` — lista eventos; exige mestre da campanha.
- `POST /campaign-audits/{audit_id}/reverse` — reverte evento elegível com motivo.

Reversões são permitidas somente quando o evento foi marcado como reversível e o estado atual ainda corresponde ao estado posterior registrado. Arquivamentos de campanha e edições de ficha feitas pelo mestre possuem aplicação inversa. A reversão preserva o evento original, registra responsável, horário e motivo, e cria um novo evento com `reversal_of_id`. Não membros recebem 404 sem confirmação da existência do evento.

## Personagens

- `POST /campaigns/{campaign_id}/characters` — cria ficha; jogador cria para si e mestre pode atribuir a mestre ou jogador da campanha.
- `GET /campaigns/{campaign_id}/characters` — mestre lista todas; jogador lista somente as próprias; observador recebe lista vazia.
- `GET /characters/{character_id}` — retorna ficha somente ao mestre da campanha ou ao jogador responsável.
- `PATCH /characters/{character_id}` — altera identidade, atributos, PV, CA, iniciativa e deslocamento.

Criação e atualização também aceitam:

- `proficiencies` — lista de categoria e nome, sem cálculo automático de bônus;
- `resources` — lista de nome, valor atual, máximo e recuperação `short_rest`, `long_rest` ou `manual`.

As listas enviadas em um `PATCH` substituem integralmente a respectiva coleção e não podem conter duplicatas. Modificadores de atributo são derivados pela API e nunca persistidos ou recalculados como fonte de verdade pelo cliente. Acesso direto sem visibilidade retorna `character_not_found` com HTTP 404. Criação e atualização registram auditoria transacional; o campo opcional `reason` documenta a motivação da edição. Atualizações executadas pelo mestre são marcadas como reversíveis e exigem que nenhuma mudança posterior tenha alterado a ficha.

## Regras puras implementadas na fundação

- `POST /rules/attacks/resolve`
- `POST /rules/durability/preview`
- `POST /rules/encumbrance/calculate`
- `POST /rules/long-rest/simulate`
- `POST /rules/progression/simulate`
- `POST /rules/progression/classes/simulate`
- `POST /rules/progression/ability-scores/simulate`
- `POST /rules/progression/subclasses/simulate`

`POST /rules/progression/simulate` recebe `current_level` e `experience_points` opcional. A resposta descreve o nível atual, o próximo nível, limiares de XP, bônus de proficiência, XP restante e qualificação. A operação avalia somente o próximo nível e não persiste mudanças. Sem XP, a qualificação é `not_evaluated`; no nível 20, é `level_cap`.

`POST /rules/progression/classes/simulate` recebe uma das doze classes SRD, nível atual nessa classe, modificador de Constituição e método de PV opcional. O método `fixed` usa o valor médio arredondado para cima; `rolled` exige que o cliente informe um resultado válido para o dado da classe. A resposta informa ganho de PV e escolhas pendentes de `hit_points` ou `ability_score_improvement`. O contrato cobre somente PV e aumento de atributo, não sinaliza conclusão integral da subida e não altera o banco.

`POST /rules/progression/ability-scores/simulate` recebe as seis pontuações atuais, os aumentos escolhidos e o nível total resultante. Aceita somente `+2` em um atributo ou `+1` em dois atributos diferentes, sem superar 20. A resposta contém pontuações e modificadores antes/depois, mudança do modificador de Constituição e ajuste correspondente do máximo de PV. A rota não valida se a classe concede a escolha naquele nível; essa composição pertence ao assistente completo.

`POST /rules/progression/subclasses/simulate` recebe classe, nível alvo nessa classe e uma subclasse selecionada opcional. A resposta informa o nível da escolha, disponibilidade, obrigatoriedade e as opções públicas do SRD 5.1. Seleções antecipadas ou pertencentes a outra classe são rejeitadas. A rota não seleciona automaticamente e não persiste dados.

## Inventário e durabilidade

- `GET /campaigns/{campaign_id}/item-catalog` — materiais e qualidades.
- `POST /campaigns/{campaign_id}/item-templates` — mestre cria modelo versionado.
- `GET /campaigns/{campaign_id}/item-templates` — lista modelos da campanha.
- `PUT /characters/{character_id}/professions` — substitui domínios profissionais.
- `POST /characters/{character_id}/items` — mestre cria instância.
- `GET /characters/{character_id}/items` — inventário com leitura de durabilidade conforme profissão.
- `PATCH /items/{item_id}` — equipa ou seleciona arma ativa.
- `POST /items/{item_id}/attacks/simulate` e `/apply` — calcula e aplica desgaste.
- `POST /items/{item_id}/repairs` — mestre repara e gera auditoria reversível.

## Notas e mídia

- `POST|GET /campaigns/{campaign_id}/notes` — cria e lista notas visíveis.
- `GET|PATCH|DELETE /notes/{note_id}` — leitura e operações exclusivas do autor.
- `POST /notes/{note_id}/media` — registra imagem e emite URL temporária de upload.
- `GET /notes/{note_id}/media/{asset_id}` — emite URL temporária de leitura.

O mestre não recebe notas privadas e não pode editar notas de outro autor.

## Painel do mestre e descanso

- `GET /campaigns/{campaign_id}/master-dashboard` — grupo ativo, recursos e equipamentos.
- `PATCH /characters/{character_id}/master-state` — seleção, dados de vida, exaustão e fadiga.
- `PUT /characters/{character_id}/spell-slots` — substitui espaços persistidos.
- `POST /characters/{character_id}/conditions` — registra condição.
- `POST /characters/{character_id}/long-rest/simulate` — simula sem mutação.
- `POST /characters/{character_id}/long-rest/apply` — aplica com `Idempotency-Key`.

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
