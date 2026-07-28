"use client";

import { FormEvent, useState } from "react";
import {
  acceptCampaignInvite,
  createCampaign,
  createCharacter,
  type Campaign,
} from "@/lib/characters";
import styles from "./Onboarding.module.css";

const classOptions = [
  "Bárbaro",
  "Bardo",
  "Clérigo",
  "Druida",
  "Guerreiro",
  "Monge",
  "Paladino",
  "Patrulheiro",
  "Ladino",
  "Feiticeiro",
  "Bruxo",
  "Mago",
];

export function Onboarding({
  displayName,
  campaigns,
  onReady,
  onLogout,
}: {
  displayName: string;
  campaigns: Campaign[];
  onReady: () => Promise<void>;
  onLogout: () => Promise<void>;
}) {
  const [mode, setMode] = useState<"character" | "invite">("character");
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function createWorkspace(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      let campaignId = String(form.get("campaign_id") ?? "");
      if (!campaignId) {
        const campaign = await createCampaign(String(form.get("campaign_name")));
        campaignId = campaign.id;
      }
      const hp = Number(form.get("hit_points"));
      await createCharacter(campaignId, {
        name: String(form.get("character_name")),
        race_name: String(form.get("race_name")),
        class_name: String(form.get("class_name")),
        background: String(form.get("background")),
        alignment: String(form.get("alignment")),
        hit_points_current: hp,
        hit_points_max: hp,
        armor_class: Number(form.get("armor_class")),
        speed_meters: Number(form.get("speed_meters")),
        abilities: {
          strength: Number(form.get("strength")),
          dexterity: Number(form.get("dexterity")),
          constitution: Number(form.get("constitution")),
          intelligence: Number(form.get("intelligence")),
          wisdom: Number(form.get("wisdom")),
          charisma: Number(form.get("charisma")),
        },
      });
      await onReady();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Não foi possível preparar a campanha.",
      );
    } finally {
      setWorking(false);
    }
  }

  async function acceptInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true);
    setError("");
    const token = String(new FormData(event.currentTarget).get("invite_token"));
    try {
      await acceptCampaignInvite(token.trim());
      setMode("character");
      await onReady();
    } catch (submissionError) {
      setError(
        submissionError instanceof Error
          ? submissionError.message
          : "Não foi possível aceitar o convite.",
      );
    } finally {
      setWorking(false);
    }
  }

  const writableCampaigns = campaigns.filter(
    (campaign) => campaign.role !== "observer",
  );

  return (
    <main className={styles.page}>
      <header>
        <div className={styles.brand}>◇ Nexus d20</div>
        <button type="button" onClick={() => void onLogout()}>Sair</button>
      </header>
      <section className={styles.card}>
        <div className={styles.intro}>
          <span>Primeiros passos</span>
          <h1>Prepare sua primeira jornada, {displayName}.</h1>
          <p>
            Crie uma campanha como mestre ou use um convite para entrar na mesa
            de outra pessoa.
          </p>
        </div>
        <div className={styles.tabs}>
          <button
            type="button"
            aria-pressed={mode === "character"}
            onClick={() => setMode("character")}
          >
            {campaigns.length ? "Criar personagem" : "Criar campanha"}
          </button>
          <button
            type="button"
            aria-pressed={mode === "invite"}
            onClick={() => setMode("invite")}
          >
            Usar convite
          </button>
        </div>

        {mode === "invite" ? (
          <form className={styles.form} onSubmit={acceptInvite}>
            <label className={styles.wide}>
              Código do convite
              <input
                name="invite_token"
                required
                minLength={20}
                maxLength={256}
                placeholder="Cole o código enviado pelo mestre"
              />
            </label>
            {error && <p className={styles.error} role="alert">{error}</p>}
            <button className={styles.primary} type="submit" disabled={working}>
              {working ? "Validando…" : "Entrar na campanha"}
            </button>
          </form>
        ) : writableCampaigns.length === 0 && campaigns.length > 0 ? (
          <div className={styles.observer}>
            <h2>Acesso de observador ativo</h2>
            <p>Observadores acompanham a campanha, mas não criam personagens.</p>
          </div>
        ) : (
          <form className={styles.form} onSubmit={createWorkspace}>
            {writableCampaigns.length ? (
              <label className={styles.wide}>
                Campanha
                <select name="campaign_id" required>
                  {writableCampaigns.map((campaign) => (
                    <option key={campaign.id} value={campaign.id}>
                      {campaign.name} · {campaign.role === "master" ? "Mestre" : "Jogador"}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <label className={styles.wide}>
                Nome da campanha
                <input
                  name="campaign_name"
                  required
                  minLength={3}
                  maxLength={160}
                  defaultValue="As Sombras de Esteren"
                />
              </label>
            )}
            <label>
              Personagem
              <input name="character_name" required minLength={2} maxLength={160} />
            </label>
            <label>
              Raça
              <input name="race_name" maxLength={120} defaultValue="Humano" />
            </label>
            <label>
              Classe
              <select name="class_name" defaultValue="Monge">
                {classOptions.map((className) => (
                  <option key={className}>{className}</option>
                ))}
              </select>
            </label>
            <label>
              Antecedente
              <input name="background" maxLength={160} defaultValue="Aventureiro" />
            </label>
            <label>
              Alinhamento
              <input name="alignment" maxLength={80} defaultValue="Neutro" />
            </label>
            <label>
              Pontos de vida
              <input name="hit_points" type="number" min={1} max={9999} defaultValue={10} />
            </label>
            <label>
              Classe de armadura
              <input name="armor_class" type="number" min={0} max={99} defaultValue={10} />
            </label>
            <label>
              Deslocamento (m)
              <input name="speed_meters" type="number" min={0} max={999} defaultValue={9} />
            </label>
            <fieldset className={styles.abilities}>
              <legend>Atributos iniciais</legend>
              {[
                ["strength", "Força"],
                ["dexterity", "Destreza"],
                ["constitution", "Constituição"],
                ["intelligence", "Inteligência"],
                ["wisdom", "Sabedoria"],
                ["charisma", "Carisma"],
              ].map(([name, label]) => (
                <label key={name}>
                  {label}
                  <input name={name} type="number" min={1} max={30} defaultValue={10} />
                </label>
              ))}
            </fieldset>
            {error && <p className={styles.error} role="alert">{error}</p>}
            <button className={styles.primary} type="submit" disabled={working}>
              {working ? "Preparando…" : "Começar a campanha"}
            </button>
          </form>
        )}
      </section>
    </main>
  );
}
