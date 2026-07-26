"use client";

import { type FormEvent, useEffect, useRef, useState } from "react";
import {
  buildCharacterUpdate,
  characterToEditValues,
  editableAbilities,
} from "@/lib/character-edit";
import {
  type Character,
  type CharacterUpdate,
  updateCharacter,
} from "@/lib/characters";
import styles from "./CharacterEditor.module.css";

type Props = {
  character: Character;
  role: "master" | "player" | "observer";
  onClose: () => void;
  onSaved: (character: Character) => void;
};

type NumberField = {
  name: keyof CharacterUpdate;
  label: string;
  min: number;
  max: number;
  suffix?: string;
};

const combatFields: NumberField[] = [
  { name: "hit_points_current", label: "PV atuais", min: 0, max: 9999 },
  { name: "hit_points_max", label: "PV máximos", min: 1, max: 9999 },
  { name: "temporary_hit_points", label: "PV temporários", min: 0, max: 9999 },
  { name: "armor_class", label: "Classe de armadura", min: 0, max: 99 },
  { name: "initiative", label: "Iniciativa", min: -20, max: 30 },
  { name: "speed_meters", label: "Deslocamento", min: 0, max: 999, suffix: "m" },
];

export function CharacterEditor({
  character,
  role,
  onClose,
  onSaved,
}: Props) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const nameInput = useRef<HTMLInputElement>(null);
  const initialValues = characterToEditValues(character);

  useEffect(() => {
    nameInput.current?.focus();
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape" && !saving) onClose();
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose, saving]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const values = Object.fromEntries(
        [...new FormData(event.currentTarget).entries()].map(([key, value]) => [
          key,
          String(value),
        ]),
      );
      const payload = buildCharacterUpdate(values);
      const updated = await updateCharacter(character.id, payload);
      onSaved(updated);
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Não foi possível salvar a ficha.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className={styles.backdrop} role="presentation">
      <section
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="character-editor-title"
      >
        <header className={styles.header}>
          <div>
            <span>Ficha inteligente</span>
            <h2 id="character-editor-title">Editar {character.name}</h2>
          </div>
          <button
            type="button"
            className={styles.close}
            onClick={onClose}
            disabled={saving}
            aria-label="Fechar editor"
          >
            ×
          </button>
        </header>

        <form onSubmit={submit}>
          <div className={styles.scrollArea}>
            <fieldset>
              <legend>Identidade</legend>
              <div className={styles.identityGrid}>
                <label className={styles.wide}>
                  Nome
                  <input
                    ref={nameInput}
                    name="name"
                    defaultValue={initialValues.name}
                    minLength={2}
                    maxLength={160}
                    required
                  />
                </label>
                <label>
                  Raça
                  <input
                    name="race_name"
                    defaultValue={initialValues.race_name}
                    maxLength={120}
                  />
                </label>
                <label>
                  Classe
                  <input
                    name="class_name"
                    defaultValue={initialValues.class_name}
                    maxLength={120}
                  />
                </label>
                <label>
                  Subclasse
                  <input
                    name="subclass_name"
                    defaultValue={initialValues.subclass_name}
                    maxLength={120}
                  />
                </label>
                <label>
                  Nível
                  <input
                    name="level"
                    type="number"
                    defaultValue={initialValues.level}
                    min={1}
                    max={20}
                    required
                  />
                </label>
                <label>
                  Antecedente
                  <input
                    name="background"
                    defaultValue={initialValues.background}
                    maxLength={160}
                  />
                </label>
                <label>
                  Alinhamento
                  <input
                    name="alignment"
                    defaultValue={initialValues.alignment}
                    maxLength={80}
                  />
                </label>
              </div>
            </fieldset>

            <fieldset>
              <legend>Combate e movimento</legend>
              <div className={styles.numberGrid}>
                {combatFields.map((field) => (
                  <label key={field.name}>
                    {field.label}
                    <span className={styles.inputWithSuffix}>
                      <input
                        name={field.name}
                        type="number"
                        defaultValue={initialValues[field.name]}
                        min={field.min}
                        max={field.max}
                        required
                      />
                      {field.suffix && <small>{field.suffix}</small>}
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>

            <fieldset>
              <legend>Atributos</legend>
              <p className={styles.hint}>
                Os modificadores serão recalculados pela API após salvar.
              </p>
              <div className={styles.abilityGrid}>
                {editableAbilities.map((ability) => (
                  <label key={ability.code}>
                    {ability.label}
                    <input
                      name={ability.code}
                      type="number"
                      defaultValue={initialValues[ability.code]}
                      min={1}
                      max={30}
                      required
                    />
                  </label>
                ))}
              </div>
            </fieldset>

            <label className={styles.reason}>
              Motivo da alteração {role === "master" && <span>recomendado ao mestre</span>}
              <textarea
                name="reason"
                defaultValue=""
                maxLength={500}
                rows={3}
                placeholder="Ex.: dano recebido durante a sessão"
              />
            </label>

            {error && (
              <p className={styles.error} role="alert">
                {error}
              </p>
            )}
          </div>

          <footer className={styles.footer}>
            <p>O salvamento gera um registro de auditoria.</p>
            <div>
              <button type="button" onClick={onClose} disabled={saving}>
                Cancelar
              </button>
              <button type="submit" className={styles.save} disabled={saving}>
                {saving ? "Salvando…" : "Salvar ficha"}
              </button>
            </div>
          </footer>
        </form>
      </section>
    </div>
  );
}
