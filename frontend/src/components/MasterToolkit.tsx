"use client";

import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import styles from "./MasterToolkit.module.css";

type LibraryEntry = {
  id: string;
  kind: string;
  name: string;
  is_identified: boolean;
};

type Shop = {
  id: string;
  name: string;
  stock: { library_entry_id: string; name: string; quantity: number }[];
};

type Creature = {
  id: string;
  name: string;
  challenge_rating: number;
  biomes: string[];
};

type KnowledgeGraph = {
  nodes: { id: string; node_type: string; title: string }[];
  edges: { id: string; relation_type: string }[];
  timeline: { id: string; title: string; occurred_at: string }[];
};

type Dashboard = {
  id: string;
  name: string;
  template_code: string;
  visibility: string;
};

const phaseLabels = [
  ["07", "Biblioteca", "Itens, magias, condições, serviços e lojas."],
  ["08", "Encontros", "Bestiário ponderado por bioma, perigo e situação."],
  ["09", "Jornada", "Carga métrica, marcha forçada, suprimentos e fadiga."],
  ["10", "Conhecimento", "Teia, linha do tempo e painéis de apresentação."],
];

const previewLibrary: LibraryEntry[] = [
  { id: "preview-item", kind: "item", name: "Relíquia de Brumaverde", is_identified: false },
  { id: "preview-spell", kind: "spell", name: "Névoa Arcana", is_identified: true },
];

const previewCreatures: Creature[] = [
  {
    id: "preview-wolf",
    name: "Lobo de Névoa",
    challenge_rating: 1,
    biomes: ["floresta"],
  },
  {
    id: "preview-guardian",
    name: "Guardião das Ruínas",
    challenge_rating: 3,
    biomes: ["ruínas"],
  },
];

export function MasterToolkit({
  campaignId,
  characterId,
  role,
}: {
  campaignId?: string;
  characterId?: string;
  role?: string;
}) {
  const [library, setLibrary] = useState<LibraryEntry[]>(previewLibrary);
  const [shops, setShops] = useState<Shop[]>([]);
  const [creatures, setCreatures] = useState<Creature[]>(previewCreatures);
  const [knowledge, setKnowledge] = useState<KnowledgeGraph>({
    nodes: [
      { id: "preview-clue", node_type: "clue", title: "Símbolos antigos" },
      { id: "preview-place", node_type: "location", title: "Ruínas Élficas" },
    ],
    edges: [{ id: "preview-edge", relation_type: "encontrado_em" }],
    timeline: [],
  });
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [entryName, setEntryName] = useState("");
  const [entryKind, setEntryKind] = useState("item");
  const [biome, setBiome] = useState("floresta");
  const [distance, setDistance] = useState("40");
  const [template, setTemplate] = useState("exploration");
  const [notice, setNotice] = useState("Aguardando uma campanha do mestre.");

  useEffect(() => {
    if (!campaignId || role !== "master") return;
    let cancelled = false;
    Promise.all([
      apiFetch<LibraryEntry[]>(`/campaigns/${campaignId}/library`),
      apiFetch<Shop[]>(`/campaigns/${campaignId}/shops`),
      apiFetch<Creature[]>(`/campaigns/${campaignId}/creatures`),
      apiFetch<KnowledgeGraph>(`/campaigns/${campaignId}/knowledge`),
      apiFetch<Dashboard[]>(`/campaigns/${campaignId}/dashboards`),
    ])
      .then(([entries, loadedShops, loadedCreatures, graph, layouts]) => {
        if (cancelled) return;
        setLibrary(entries);
        setShops(loadedShops);
        setCreatures(loadedCreatures);
        setKnowledge(graph);
        setDashboards(layouts);
        setNotice("Ferramentas do mestre sincronizadas.");
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setNotice(error instanceof Error ? error.message : "Falha ao sincronizar.");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [campaignId, role]);

  if (role && role !== "master") return null;
  const preview = !campaignId;

  async function createEntry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!campaignId || !entryName.trim()) return;
    try {
      const entry = await apiFetch<LibraryEntry>(`/campaigns/${campaignId}/library`, {
        method: "POST",
        body: JSON.stringify({
          kind: entryKind,
          name: entryName.trim(),
          description: "",
          data: {},
        }),
      });
      setLibrary((current) => [...current, entry]);
      setEntryName("");
      setNotice(`${entry.name} foi adicionado à biblioteca.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao criar entrada.");
    }
  }

  async function generateEncounter() {
    if (!campaignId) return;
    try {
      const encounter = await apiFetch<{
        creatures: { id: string; name: string }[];
        estimated_difficulty: string;
      }>(`/campaigns/${campaignId}/encounters/generate`, {
        method: "POST",
        body: JSON.stringify({
          biome,
          danger: 2,
          seed: Date.now() % 2_147_483_647,
        }),
      });
      setNotice(
        `Encontro ${encounter.estimated_difficulty}: ` +
          encounter.creatures.map((creature) => creature.name).join(", "),
      );
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao gerar encontro.");
    }
  }

  async function planJourney() {
    if (!campaignId || !characterId) return;
    try {
      const plan = await apiFetch<{
        estimated_days: string;
        daily_distance_km: string;
      }>(`/campaigns/${campaignId}/travel-plans`, {
        method: "POST",
        body: JSON.stringify({
          name: "Jornada planejada no painel",
          origin: "Ponto atual",
          destination: "Destino da campanha",
          distance_km: distance,
          pace: "normal",
          traveler_ids: [characterId],
          travel_hours_per_day: 8,
        }),
      });
      setNotice(
        `Jornada: ${plan.estimated_days} dias, ${plan.daily_distance_km} km/dia.`,
      );
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao planejar viagem.");
    }
  }

  async function createDashboard() {
    if (!campaignId) return;
    try {
      const dashboard = await apiFetch<Dashboard>(
        `/campaigns/${campaignId}/dashboards`,
        {
          method: "POST",
          body: JSON.stringify({
            name: `Painel ${template}`,
            template_code: template,
            visibility: "presentation",
            cards: knowledge.nodes.slice(0, 4).map((node) => ({
              title: node.title,
              node_type: node.node_type,
            })),
          }),
        },
      );
      setDashboards((current) => [...current, dashboard]);
      setNotice("Painel criado com filtragem pública no servidor.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Falha ao criar painel.");
    }
  }

  return (
    <section className={styles.toolkit} aria-label="Central do mestre">
      <header className={styles.header}>
        <div>
          <span>Fases 7–10</span>
          <h2>Central de preparação e mundo</h2>
        </div>
        <small>{notice}</small>
      </header>

      <div className={styles.phaseRail}>
        {phaseLabels.map(([number, title, description]) => (
          <div key={number}>
            <b>{number}</b>
            <span>
              <strong>{title}</strong>
              <small>{description}</small>
            </span>
          </div>
        ))}
      </div>

      <div className={styles.grid}>
        <article className={styles.panel}>
          <div className={styles.panelHeading}>
            <span>Biblioteca do mestre</span>
            <b>{library.length + shops.length}</b>
          </div>
          <form className={styles.inlineForm} onSubmit={createEntry}>
            <select value={entryKind} onChange={(event) => setEntryKind(event.target.value)}>
              <option value="item">Item</option>
              <option value="spell">Magia</option>
              <option value="condition">Condição</option>
              <option value="service">Serviço</option>
            </select>
            <input
              value={entryName}
              onChange={(event) => setEntryName(event.target.value)}
              placeholder="Nome da nova entrada"
              maxLength={160}
              disabled={preview}
            />
            <button type="submit" disabled={preview || !entryName.trim()}>
              Adicionar
            </button>
          </form>
          <ul>
            {library.slice(0, 4).map((entry) => (
              <li key={entry.id}>
                <strong>{entry.name}</strong>
                <small>{entry.kind} · {entry.is_identified ? "identificado" : "oculto"}</small>
              </li>
            ))}
          </ul>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeading}>
            <span>Bestiário e encontros</span>
            <b>{creatures.length}</b>
          </div>
          <label>
            Bioma
            <input value={biome} onChange={(event) => setBiome(event.target.value)} />
          </label>
          <button
            className={styles.primaryAction}
            type="button"
            onClick={() => void generateEncounter()}
            disabled={preview || creatures.length === 0}
          >
            Gerar encontro ponderado
          </button>
          <ul>
            {creatures.slice(0, 4).map((creature) => (
              <li key={creature.id}>
                <strong>{creature.name}</strong>
                <small>ND {creature.challenge_rating} · {creature.biomes.join(", ")}</small>
              </li>
            ))}
          </ul>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeading}>
            <span>Viagem e fadiga</span>
            <b>kg</b>
          </div>
          <label>
            Distância em quilômetros
            <input
              type="number"
              min="1"
              step="0.1"
              value={distance}
              onChange={(event) => setDistance(event.target.value)}
            />
          </label>
          <button
            className={styles.primaryAction}
            type="button"
            onClick={() => void planJourney()}
            disabled={!characterId || Number(distance) <= 0}
          >
            Calcular jornada
          </button>
          <p>
            Considera carga pessoal, personagem limitante, marcha forçada,
            alimento, água e fadiga oculta opcional.
          </p>
        </article>

        <article className={styles.panel}>
          <div className={styles.panelHeading}>
            <span>Teia e painéis</span>
            <b>{knowledge.nodes.length}</b>
          </div>
          <label>
            Modelo
            <select value={template} onChange={(event) => setTemplate(event.target.value)}>
              <option value="combat">Combate</option>
              <option value="city">Cidade</option>
              <option value="shop">Loja</option>
              <option value="exploration">Exploração</option>
              <option value="rest">Descanso</option>
            </select>
          </label>
          <button
            className={styles.primaryAction}
            type="button"
            onClick={() => void createDashboard()}
            disabled={preview}
          >
            Criar painel apresentável
          </button>
          <div className={styles.metrics}>
            <span>{knowledge.edges.length} conexões</span>
            <span>{knowledge.timeline.length} eventos</span>
            <span>{dashboards.length} painéis</span>
          </div>
        </article>
      </div>
    </section>
  );
}
