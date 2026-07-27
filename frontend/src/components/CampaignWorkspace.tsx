"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { LevelUpAssistant } from "./LevelUpAssistant";
import styles from "./CampaignWorkspace.module.css";

type Item = {
  id: string;
  name: string;
  category: string;
  equipped: boolean;
  is_magical: boolean;
  durability: {
    state: string;
    percentage: number | null;
    current_points: number | null;
    maximum_points: number | null;
    break_risk: boolean;
  };
};

type Note = {
  id: string;
  title: string;
  body: string;
  visibility: string;
};

type DashboardCharacter = {
  id: string;
  name: string;
  hit_points: { current: number; maximum: number };
  exhaustion_level: number;
  active_items: { id: string; name: string }[];
};

export function CampaignWorkspace({
  campaignId,
  characterId,
  role,
}: {
  campaignId?: string;
  characterId?: string;
  role?: string;
}) {
  const [items, setItems] = useState<Item[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [group, setGroup] = useState<DashboardCharacter[]>([]);
  const [notice, setNotice] = useState("Recursos avançados disponíveis após entrar.");
  const [noteTitle, setNoteTitle] = useState("");
  const [restPreview, setRestPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!campaignId || !characterId) return;
    let cancelled = false;
    Promise.all([
      apiFetch<Item[]>(`/characters/${characterId}/items`),
      apiFetch<Note[]>(`/campaigns/${campaignId}/notes`),
      role === "master"
        ? apiFetch<{ characters: DashboardCharacter[] }>(
            `/campaigns/${campaignId}/master-dashboard`,
          )
        : Promise.resolve({ characters: [] }),
    ])
      .then(([loadedItems, loadedNotes, dashboard]) => {
        if (cancelled) return;
        setItems(loadedItems);
        setNotes(loadedNotes);
        setGroup(dashboard.characters);
        setNotice("Inventário, notas e campanha sincronizados.");
      })
      .catch((error: unknown) => {
        if (!cancelled)
          setNotice(error instanceof Error ? error.message : "Falha ao sincronizar.");
      });
    return () => {
      cancelled = true;
    };
  }, [campaignId, characterId, role]);

  async function createNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!campaignId || !noteTitle.trim()) return;
    try {
      const note = await apiFetch<Note>(`/campaigns/${campaignId}/notes`, {
        method: "POST",
        body: JSON.stringify({
          title: noteTitle,
          body: "",
          visibility: "private",
          links: characterId
            ? [{ entity_type: "character", entity_id: characterId }]
            : [],
        }),
      });
      setNotes((current) => [note, ...current]);
      setNoteTitle("");
      setNotice("Nota privada criada.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Não foi possível criar a nota.");
    }
  }

  async function simulateRest() {
    if (!characterId) return;
    try {
      const preview = await apiFetch<{
        result: { hit_points_after: number; warnings: string[] };
        expired_conditions: string[];
      }>(`/characters/${characterId}/long-rest/simulate`, {
        method: "POST",
        body: JSON.stringify({
          has_sufficient_food: true,
          has_sufficient_water: true,
          rest_completed: true,
          antimagic_zone: false,
        }),
      });
      setRestPreview(
        `PV após descanso: ${preview.result.hit_points_after}. ` +
          (preview.result.warnings.join(" ") || "Nenhum alerta."),
      );
    } catch (error) {
      setRestPreview(
        error instanceof Error ? error.message : "Não foi possível simular.",
      );
    }
  }

  return (
    <section className={styles.workspace} aria-label="Recursos da campanha">
      <header className={styles.heading}>
        <div>
          <span>Campanha viva</span>
          <h2>Inventário, registros e controle</h2>
        </div>
        <small>{notice}</small>
      </header>

      <div className={styles.grid}>
        {characterId && (
          <article className={styles.panel}>
            <div className={styles.panelTitle}>
              <div>
                <span>Evolução</span>
                <h3>Subir de nível</h3>
              </div>
              <b>03</b>
            </div>
            <LevelUpAssistant characterId={characterId} />
          </article>
        )}
        <article className={styles.panel}>
          <div className={styles.panelTitle}>
            <div>
              <span>Equipamento</span>
              <h3>Durabilidade</h3>
            </div>
            <b>{items.length}</b>
          </div>
          {items.length === 0 ? (
            <p className={styles.empty}>Nenhum item atribuído ao personagem.</p>
          ) : (
            <ul className={styles.itemList}>
              {items.slice(0, 5).map((item) => {
                const percentage = item.durability.percentage;
                return (
                  <li key={item.id}>
                    <div>
                      <strong>{item.name}</strong>
                      <small>{item.durability.state}</small>
                    </div>
                    <span>
                      {percentage === null ? "Leitura estimada" : `${percentage}%`}
                    </span>
                    <i aria-hidden="true">
                      <i style={{ width: `${percentage ?? 35}%` }} />
                    </i>
                  </li>
                );
              })}
            </ul>
          )}
        </article>

        <article className={styles.panel}>
          <div className={styles.panelTitle}>
            <div>
              <span>Crônicas</span>
              <h3>Notas recentes</h3>
            </div>
            <b>{notes.length}</b>
          </div>
          <form className={styles.noteForm} onSubmit={createNote}>
            <input
              value={noteTitle}
              onChange={(event) => setNoteTitle(event.target.value)}
              placeholder="Nova nota privada…"
              disabled={!campaignId}
              maxLength={200}
            />
            <button type="submit" disabled={!campaignId || !noteTitle.trim()}>
              +
            </button>
          </form>
          <ul className={styles.noteList}>
            {notes.slice(0, 4).map((note) => (
              <li key={note.id}>
                <span aria-hidden="true">{note.visibility === "private" ? "◆" : "◇"}</span>
                <div>
                  <strong>{note.title}</strong>
                  <small>
                    {note.visibility === "private" ? "Somente você" : "Compartilhada"}
                  </small>
                </div>
              </li>
            ))}
          </ul>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelTitle}>
            <div>
              <span>Mestre</span>
              <h3>Grupo ativo</h3>
            </div>
            <b>{group.length}</b>
          </div>
          {role !== "master" ? (
            <p className={styles.empty}>Visível apenas para o mestre da campanha.</p>
          ) : (
            <>
              <ul className={styles.groupList}>
                {group.slice(0, 4).map((member) => (
                  <li key={member.id}>
                    <strong>{member.name}</strong>
                    <span>
                      PV {member.hit_points.current}/{member.hit_points.maximum}
                    </span>
                    <small>Exaustão {member.exhaustion_level}</small>
                  </li>
                ))}
              </ul>
              <button
                className={styles.restButton}
                type="button"
                onClick={() => void simulateRest()}
                disabled={!characterId}
              >
                Simular descanso longo
              </button>
              {restPreview && <p className={styles.preview}>{restPreview}</p>}
            </>
          )}
        </article>
      </div>
    </section>
  );
}
