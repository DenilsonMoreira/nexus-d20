"use client";

import { useCallback, useEffect, useState } from "react";
import { AbilityRadar } from "@/components/AbilityRadar";
import {
  type ActiveCharacter,
  type Character,
  loadActiveCharacter,
} from "@/lib/characters";
import styles from "./page.module.css";

const demoCharacter: Character = {
  id: "demo",
  campaign_id: "demo",
  owner_user_id: "demo",
  name: "Nox Brasalume",
  race_name: "Humano variante",
  class_name: "Monge",
  subclass_name: "",
  level: 2,
  background: "Forasteiro",
  alignment: "Neutro",
  hit_points_current: 17,
  hit_points_max: 17,
  temporary_hit_points: 0,
  armor_class: 16,
  initiative: 3,
  speed_meters: 9,
  abilities: [
    { code: "charisma", label: "CARISMA", score: 8, modifier: -1 },
    { code: "intelligence", label: "INTELIGÊNCIA", score: 10, modifier: 0 },
    { code: "wisdom", label: "SABEDORIA", score: 15, modifier: 2 },
    { code: "strength", label: "FORÇA", score: 12, modifier: 1 },
    { code: "dexterity", label: "DESTREZA", score: 16, modifier: 3 },
    { code: "constitution", label: "CONSTITUIÇÃO", score: 14, modifier: 2 },
  ],
};

function formatModifier(value: number) {
  return value >= 0 ? `+${value}` : String(value);
}

const abilityOrder = [
  "charisma",
  "intelligence",
  "wisdom",
  "strength",
  "dexterity",
  "constitution",
];

export default function Home() {
  const [active, setActive] = useState<ActiveCharacter | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(
    "Conectando a ficha ao cofre da campanha…",
  );

  const loadCharacter = useCallback(async () => {
    setLoading(true);
    try {
      const result = await loadActiveCharacter();
      setActive(result);
      setMessage(
        result
          ? "Ficha sincronizada com a campanha"
          : "Nenhuma ficha disponível nesta conta",
      );
    } catch {
      setActive(null);
      setMessage("Prévia visual — entre para carregar sua ficha");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    void loadActiveCharacter()
      .then((result) => {
        if (cancelled) return;
        setActive(result);
        setMessage(
          result
            ? "Ficha sincronizada com a campanha"
            : "Nenhuma ficha disponível nesta conta",
        );
      })
      .catch(() => {
        if (cancelled) return;
        setActive(null);
        setMessage("Prévia visual — entre para carregar sua ficha");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const character = active?.character ?? demoCharacter;
  const orderedAbilities = [...character.abilities].sort(
    (left, right) =>
      abilityOrder.indexOf(left.code) - abilityOrder.indexOf(right.code),
  );
  const campaignName = active?.campaign.name ?? "As Sombras de Esteren";
  const characterSubtitle = [
    character.class_name && `${character.class_name} ${character.level}`,
    character.race_name,
    character.alignment,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <main className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span aria-hidden="true">◇</span>
          Nexus d20
        </div>
        <nav aria-label="Navegação principal">
          {["Ficha", "Evolução", "Magias", "Inventário", "Notas", "Campanha"].map(
            (item, index) => (
              <button
                className={index === 0 ? styles.activeNav : styles.navItem}
                key={item}
                type="button"
                disabled={index !== 0}
              >
                {item}
              </button>
            ),
          )}
        </nav>
        <div className={styles.campaign}>
          <span>Campanha ativa</span>
          <strong>{campaignName}</strong>
          <small>D&amp;D 5e (2014)</small>
        </div>
      </aside>

      <section className={styles.content}>
        <header className={styles.header}>
          <div>
            <small>Ficha inteligente</small>
            <h1>{campaignName}</h1>
          </div>
          <button
            className={active ? styles.syncedStatus : styles.previewStatus}
            type="button"
            onClick={() => void loadCharacter()}
            disabled={loading}
          >
            <span aria-hidden="true">{active ? "●" : "◇"}</span>
            {loading ? "Sincronizando…" : message}
          </button>
        </header>

        <div className={styles.sheetGrid}>
          <article className={`${styles.card} ${styles.identityCard}`}>
            <div className={styles.characterTop}>
              <div className={styles.avatar} aria-hidden="true">
                {character.name
                  .split(" ")
                  .slice(0, 2)
                  .map((part) => part[0])
                  .join("")}
              </div>
              <div>
                <span className={styles.eyebrow}>Personagem ativo</span>
                <h2>{character.name}</h2>
                <p>{characterSubtitle}</p>
              </div>
            </div>

            <dl className={styles.stats}>
              <div>
                <dt>PV atuais</dt>
                <dd>
                  {character.hit_points_current}
                  <small> / {character.hit_points_max}</small>
                </dd>
              </div>
              <div>
                <dt>Classe de armadura</dt>
                <dd>{character.armor_class}</dd>
              </div>
              <div>
                <dt>Movimento</dt>
                <dd>
                  {character.speed_meters} <small>m</small>
                </dd>
              </div>
              <div>
                <dt>Iniciativa</dt>
                <dd>{formatModifier(character.initiative)}</dd>
              </div>
            </dl>

            <div className={styles.vitalBar}>
              <span
                style={{
                  width: `${Math.min(
                    100,
                    (character.hit_points_current / character.hit_points_max) * 100,
                  )}%`,
                }}
              />
            </div>

            <div className={styles.identityDetails}>
              <div>
                <span>Antecedente</span>
                <strong>{character.background || "Não informado"}</strong>
              </div>
              <div>
                <span>PV temporários</span>
                <strong>{character.temporary_hit_points}</strong>
              </div>
            </div>
          </article>

          <article className={`${styles.card} ${styles.radarCard}`}>
            <AbilityRadar abilities={orderedAbilities} />
          </article>

          <article className={`${styles.card} ${styles.summaryCard}`}>
            <div className={styles.cardHeader}>
              <div>
                <span className={styles.eyebrow}>Leitura rápida</span>
                <h2>Resumo da ficha</h2>
              </div>
              <span className={styles.levelSeal}>NV {character.level}</span>
            </div>
            <div className={styles.summaryList}>
              {orderedAbilities.map((ability) => (
                <div key={ability.code}>
                  <span>{ability.label}</span>
                  <strong>{ability.score}</strong>
                  <small>{formatModifier(ability.modifier)}</small>
                </div>
              ))}
            </div>
            <p className={styles.auditNote}>
              Alterações mecânicas ficam registradas no histórico da campanha.
            </p>
          </article>
        </div>
      </section>

      <nav className={styles.mobileNav} aria-label="Navegação móvel">
        {["Ficha", "Evolução", "Magias", "Inventário", "Campanha"].map(
          (item, index) => (
            <button
              type="button"
              key={item}
              className={index === 0 ? styles.mobileActive : undefined}
              disabled={index !== 0}
            >
              <span aria-hidden="true">
                {["◇", "↟", "✦", "□", "⌂"][index]}
              </span>
              {item}
            </button>
          ),
        )}
      </nav>
    </main>
  );
}
