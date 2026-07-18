# Modelo de dados conceitual

## Identidade e campanhas

- users
- sessions
- campaigns
- campaign_members
- invites
- audit_logs

## Personagem

- characters
- character_abilities
- character_classes
- character_levels
- character_proficiencies
- character_resources
- character_conditions
- character_professions
- character_spell_slots
- character_spells

## Regras

- rulesets
- rule_definitions
- rule_versions
- rule_overrides
- class_templates
- class_features
- progression_tables
- spell_templates
- condition_templates

## Inventário

- materials
- quality_levels
- item_templates
- item_template_versions
- item_instances
- item_instance_overrides
- inventory_locations
- durability_events
- repair_events
- price_entries
- shops
- shop_inventory

## Notas e mídia

- notes
- note_shares
- note_links
- media_assets

## Mestre

- creature_templates
- creature_actions
- creature_equipment
- biomes
- biome_encounter_entries
- encounter_templates
- encounter_instances
- encounter_participants
- knowledge_nodes
- knowledge_edges
- timeline_events
- dashboard_layouts
- dashboard_widgets

## Regras estruturais

- IDs UUID v7 quando a biblioteca adotada estiver estável; inicialmente UUID v4.
- Todas as tabelas de campanha possuem `campaign_id`.
- Templates públicos podem ter `campaign_id` nulo e `source` explícito.
- Instâncias sempre apontam para uma versão de template.
- Eventos armazenam snapshot dos parâmetros usados.
- Não sobrescrever histórico por mudança futura de regra.

## Índices prioritários

- `(campaign_id, id)` em entidades de campanha.
- `(owner_user_id, visibility)` em notas.
- `(campaign_id, category, name)` em templates.
- `(item_instance_id, created_at)` em durabilidade.
- GIN para tags e busca textual em português.
