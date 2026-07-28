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

type CampaignMember = {
  user_id: string;
  email: string;
  display_name: string;
  role: "master" | "player" | "observer";
};

type InviteResult = {
  token: string;
  role: "master" | "player" | "observer";
  expires_at: string;
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
  const [members, setMembers] = useState<CampaignMember[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"player" | "observer">("player");
  const [inviteToken, setInviteToken] = useState("");

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
      role === "master"
        ? apiFetch<{ items: CampaignMember[] }>(
            `/campaigns/${campaignId}/members`,
          )
        : Promise.resolve({ items: [] }),
    ])
      .then(([loadedItems, loadedNotes, dashboard, campaignMembers]) => {
        if (cancelled) return;
        setItems(loadedItems);
        setNotes(loadedNotes);
        setGroup(dashboard.characters);
        setMembers(campaignMembers.items);
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

  async function createInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!campaignId || !inviteEmail.trim()) return;
    try {
      const invite = await apiFetch<InviteResult>(
        `/campaigns/${campaignId}/invites`,
        {
          method: "POST",
          body: JSON.stringify({
            email: inviteEmail.trim(),
            role: inviteRole,
          }),
        },
      );
      setInviteToken(invite.token);
      setNotice(
        `Convite de ${inviteRole === "player" ? "jogador" : "observador"} gerado.`,
      );
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Não foi possível gerar o convite.",
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
        <article className={styles.panel}>
          <div className={styles.panelTitle}>
            <div>
              <span>Acesso</span>
              <h3>Participantes</h3>
            </div>
            <b>{members.length || (role ? 1 : 0)}</b>
          </div>
          {role === "master" ? (
            <>
              <ul className={styles.memberList}>
                {members.map((member) => (
                  <li key={member.user_id}>
                    <div>
                      <strong>{member.display_name}</strong>
                      <small>{member.email}</small>
                    </div>
                    <span>
                      {member.role === "master"
                        ? "Mestre"
                        : member.role === "player"
                          ? "Jogador"
                          : "Observador"}
                    </span>
                  </li>
                ))}
              </ul>
              <form className={styles.inviteForm} onSubmit={createInvite}>
                <input
                  aria-label="E-mail do convidado"
                  type="email"
                  value={inviteEmail}
                  onChange={(event) => setInviteEmail(event.target.value)}
                  placeholder="jogador@exemplo.com"
                  required
                />
                <select
                  aria-label="Papel do convidado"
                  value={inviteRole}
                  onChange={(event) =>
                    setInviteRole(event.target.value as "player" | "observer")
                  }
                >
                  <option value="player">Jogador</option>
                  <option value="observer">Observador</option>
                </select>
                <button type="submit">Gerar convite</button>
              </form>
              {inviteToken && (
                <p className={styles.inviteResult}>
                  Código de convite
                  <code>{inviteToken}</code>
                </p>
              )}
            </>
          ) : (
            <p className={styles.empty}>
              {role === "observer"
                ? "Observador: acesso somente para consulta."
                : "Jogador: você pode visualizar e editar somente sua própria ficha."}
            </p>
          )}
        </article>
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
