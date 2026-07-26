import type { Character, CharacterUpdate } from "./characters";

export const editableAbilities = [
  { code: "strength", label: "Força" },
  { code: "dexterity", label: "Destreza" },
  { code: "constitution", label: "Constituição" },
  { code: "intelligence", label: "Inteligência" },
  { code: "wisdom", label: "Sabedoria" },
  { code: "charisma", label: "Carisma" },
] as const;

export type CharacterEditValues = Record<string, string>;

export function characterToEditValues(character: Character): CharacterEditValues {
  const values: CharacterEditValues = {
    name: character.name,
    race_name: character.race_name,
    class_name: character.class_name,
    subclass_name: character.subclass_name,
    level: String(character.level),
    background: character.background,
    alignment: character.alignment,
    hit_points_current: String(character.hit_points_current),
    hit_points_max: String(character.hit_points_max),
    temporary_hit_points: String(character.temporary_hit_points),
    armor_class: String(character.armor_class),
    initiative: String(character.initiative),
    speed_meters: String(character.speed_meters),
    reason: "",
  };
  for (const ability of character.abilities) {
    values[ability.code] = String(ability.score);
  }
  return values;
}

function integerInRange(
  values: CharacterEditValues,
  field: string,
  label: string,
  minimum: number,
  maximum: number,
): number {
  const value = Number(values[field]);
  if (!Number.isInteger(value) || value < minimum || value > maximum) {
    throw new Error(`${label} deve estar entre ${minimum} e ${maximum}.`);
  }
  return value;
}

export function buildCharacterUpdate(
  values: CharacterEditValues,
): CharacterUpdate {
  const name = values.name?.trim() ?? "";
  if (name.length < 2) {
    throw new Error("Informe um nome com pelo menos 2 caracteres.");
  }
  const hitPointsCurrent = integerInRange(
    values,
    "hit_points_current",
    "PV atuais",
    0,
    9999,
  );
  const hitPointsMax = integerInRange(
    values,
    "hit_points_max",
    "PV máximos",
    1,
    9999,
  );
  if (hitPointsCurrent > hitPointsMax) {
    throw new Error("PV atuais não podem superar os PV máximos.");
  }

  return {
    name,
    race_name: values.race_name?.trim() ?? "",
    class_name: values.class_name?.trim() ?? "",
    subclass_name: values.subclass_name?.trim() ?? "",
    level: integerInRange(values, "level", "Nível", 1, 20),
    background: values.background?.trim() ?? "",
    alignment: values.alignment?.trim() ?? "",
    hit_points_current: hitPointsCurrent,
    hit_points_max: hitPointsMax,
    temporary_hit_points: integerInRange(
      values,
      "temporary_hit_points",
      "PV temporários",
      0,
      9999,
    ),
    armor_class: integerInRange(
      values,
      "armor_class",
      "Classe de armadura",
      0,
      99,
    ),
    initiative: integerInRange(
      values,
      "initiative",
      "Iniciativa",
      -20,
      30,
    ),
    speed_meters: integerInRange(
      values,
      "speed_meters",
      "Deslocamento",
      0,
      999,
    ),
    abilities: Object.fromEntries(
      editableAbilities.map(({ code, label }) => [
        code,
        integerInRange(values, code, label, 1, 30),
      ]),
    ),
    ...(values.reason?.trim() ? { reason: values.reason.trim() } : {}),
  };
}
