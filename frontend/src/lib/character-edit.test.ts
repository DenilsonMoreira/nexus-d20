import { describe, expect, it } from "vitest";
import { buildCharacterUpdate } from "./character-edit";

const validValues = {
  name: "Nox Brasalume",
  race_name: "Humano variante",
  class_name: "Monge",
  subclass_name: "",
  level: "2",
  background: "Forasteiro",
  alignment: "Neutro",
  hit_points_current: "12",
  hit_points_max: "17",
  temporary_hit_points: "0",
  armor_class: "16",
  initiative: "3",
  speed_meters: "9",
  strength: "12",
  dexterity: "16",
  constitution: "14",
  intelligence: "10",
  wisdom: "15",
  charisma: "8",
  proficiencies_json: JSON.stringify([
    { category: "skill", name: "Acrobacia" },
  ]),
  resources_json: JSON.stringify([
    {
      name: "Ki",
      current_value: 2,
      maximum_value: 2,
      recovery: "short_rest",
    },
  ]),
  reason: "Dano sofrido na sessão",
};

describe("edição da ficha", () => {
  it("serializa todos os campos sem calcular modificadores no cliente", () => {
    const payload = buildCharacterUpdate(validValues);

    expect(payload.abilities).toEqual({
      strength: 12,
      dexterity: 16,
      constitution: 14,
      intelligence: 10,
      wisdom: 15,
      charisma: 8,
    });
    expect(payload.reason).toBe("Dano sofrido na sessão");
    expect(payload.proficiencies[0].name).toBe("Acrobacia");
    expect(payload.resources[0].recovery).toBe("short_rest");
    expect(payload).not.toHaveProperty("modifier");
  });

  it("bloqueia PV atuais superiores aos máximos", () => {
    expect(() =>
      buildCharacterUpdate({
        ...validValues,
        hit_points_current: "18",
      }),
    ).toThrow("PV atuais não podem superar os PV máximos.");
  });

  it("bloqueia recurso atual superior ao máximo", () => {
    expect(() =>
      buildCharacterUpdate({
        ...validValues,
        resources_json: JSON.stringify([
          {
            name: "Ki",
            current_value: 3,
            maximum_value: 2,
            recovery: "short_rest",
          },
        ]),
      }),
    ).toThrow("Revise os valores atuais e máximos dos recursos.");
  });
});
