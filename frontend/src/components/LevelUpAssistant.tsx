"use client";

import { FormEvent, useState } from "react";
import { apiFetch } from "@/lib/api";
import styles from "./LevelUpAssistant.module.css";

const classes = [
  ["barbarian", "Bárbaro"],
  ["bard", "Bardo"],
  ["cleric", "Clérigo"],
  ["druid", "Druida"],
  ["fighter", "Guerreiro"],
  ["monk", "Monge"],
  ["paladin", "Paladino"],
  ["ranger", "Patrulheiro"],
  ["rogue", "Ladino"],
  ["sorcerer", "Feiticeiro"],
  ["warlock", "Bruxo"],
  ["wizard", "Mago"],
] as const;

const subclasses: Record<string, string> = {
  barbarian: "path_of_the_berserker",
  bard: "college_of_lore",
  cleric: "life_domain",
  druid: "circle_of_the_land",
  fighter: "champion",
  monk: "way_of_the_open_hand",
  paladin: "oath_of_devotion",
  ranger: "hunter",
  rogue: "thief",
  sorcerer: "draconic_bloodline",
  warlock: "the_fiend",
  wizard: "school_of_evocation",
};

type Preview = {
  resulting_level: number;
  target_class_level: number;
  hit_point_gain: number | null;
  proficiency_bonus_after: number;
  required_choices: string[];
  warnings: string[];
  ready_to_apply: boolean;
  spellcasting: {
    mode: string;
    cantrips_known: number;
    spells_known: number | null;
    prepared_limit: number | null;
    slots: Record<string, number>;
  };
};

export function LevelUpAssistant({ characterId }: { characterId: string }) {
  const [baseClass, setBaseClass] = useState("monk");
  const [targetClass, setTargetClass] = useState("monk");
  const [ability, setAbility] = useState("dexterity");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [notice, setNotice] = useState("");
  const [working, setWorking] = useState(false);

  function payload(resolveChoices: boolean, choices?: string[]) {
    const required = choices ?? preview?.required_choices ?? [];
    return {
      target_class_id: targetClass,
      base_class_id: baseClass,
      hit_point_method: "fixed",
      selected_subclass_id:
        resolveChoices && required.includes("subclass")
          ? subclasses[targetClass]
          : undefined,
      ability_increases:
        resolveChoices && required.includes("ability_score_improvement")
          ? { [ability]: 2 }
          : undefined,
    };
  }

  async function simulate(event?: FormEvent) {
    event?.preventDefault();
    setWorking(true);
    setNotice("");
    try {
      let result = await apiFetch<Preview>(
        `/characters/${characterId}/level-up/simulate`,
        { method: "POST", body: JSON.stringify(payload(false)) },
      );
      setPreview(result);
      if (result.required_choices.some((choice) => choice !== "hit_points")) {
        result = await apiFetch<Preview>(
          `/characters/${characterId}/level-up/simulate`,
          { method: "POST", body: JSON.stringify(payload(true, result.required_choices)) },
        );
        setPreview(result);
      }
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao simular.");
    } finally {
      setWorking(false);
    }
  }

  async function apply() {
    setWorking(true);
    try {
      const result = await apiFetch<Preview>(
        `/characters/${characterId}/level-up/apply`,
        {
          method: "POST",
          headers: { "Idempotency-Key": crypto.randomUUID() },
          body: JSON.stringify(payload(true)),
        },
      );
      setPreview(result);
      setNotice(`Nível ${result.resulting_level} aplicado e auditado.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao aplicar.");
    } finally {
      setWorking(false);
    }
  }

  return (
    <form className={styles.assistant} onSubmit={(event) => void simulate(event)}>
      <div className={styles.fields}>
        <label>
          Classe-base
          <select value={baseClass} onChange={(event) => setBaseClass(event.target.value)}>
            {classes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <label>
          Próximo nível em
          <select value={targetClass} onChange={(event) => setTargetClass(event.target.value)}>
            {classes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <label>
          Aumento +2, se exigido
          <select value={ability} onChange={(event) => setAbility(event.target.value)}>
            <option value="strength">Força</option>
            <option value="dexterity">Destreza</option>
            <option value="constitution">Constituição</option>
            <option value="intelligence">Inteligência</option>
            <option value="wisdom">Sabedoria</option>
            <option value="charisma">Carisma</option>
          </select>
        </label>
      </div>
      <div className={styles.actions}>
        <button type="submit" disabled={working}>Simular</button>
        <button
          type="button"
          disabled={working || !preview?.ready_to_apply}
          onClick={() => void apply()}
        >
          Confirmar evolução
        </button>
      </div>
      {preview && (
        <div className={styles.preview}>
          <strong>Nível total {preview.resulting_level}</strong>
          <span>Classe {preview.target_class_level} · +{preview.hit_point_gain ?? "?"} PV</span>
          <span>Proficiência +{preview.proficiency_bonus_after}</span>
          <span>
            Magia: {preview.spellcasting.mode} · espaços{" "}
            {Object.entries(preview.spellcasting.slots)
              .map(([level, count]) => `${level}º:${count}`)
              .join(" · ") || "nenhum"}
          </span>
          {preview.required_choices.length > 0 && (
            <small>Escolhas pendentes: {preview.required_choices.join(", ")}</small>
          )}
          {preview.warnings.map((warning) => <small key={warning}>{warning}</small>)}
        </div>
      )}
      {notice && <p className={styles.notice}>{notice}</p>}
    </form>
  );
}
