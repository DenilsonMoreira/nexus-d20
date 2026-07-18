import { AbilityRadar } from "@/components/AbilityRadar";
import { DurabilityCard } from "@/components/DurabilityCard";
import { MasterGroupCard } from "@/components/MasterGroupCard";
import styles from "./page.module.css";

const abilities = [
  { label: "CARISMA", score: 8, modifier: -1 },
  { label: "INTELIGÊNCIA", score: 10, modifier: 0 },
  { label: "SABEDORIA", score: 15, modifier: 2 },
  { label: "FORÇA", score: 12, modifier: 1 },
  { label: "DESTREZA", score: 16, modifier: 3 },
  { label: "CONSTITUIÇÃO", score: 14, modifier: 2 },
];

export default function Home() {
  return (
    <main className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}><span>◇</span>Nexus d20</div>
        <nav aria-label="Navegação principal">
          {['Ficha','Evolução','Magias','Inventário','Durabilidade','Notas','Campanha','Mestre'].map((item, index) => (
            <button className={index === 0 ? styles.activeNav : styles.navItem} key={item}>{item}</button>
          ))}
        </nav>
        <div className={styles.campaign}>Campanha ativa<strong>As Sombras de Esteren</strong><small>D&D 5e (2014)</small></div>
      </aside>

      <section className={styles.content}>
        <header className={styles.header}>
          <div><small>Campanha</small><h1>Painel da sessão</h1></div>
          <span className={styles.status}>API pronta para regras</span>
        </header>

        <div className={styles.gridTop}>
          <article className={styles.card}>
            <div className={styles.characterTop}>
              <div className={styles.avatar}>NB</div>
              <div><h2>Nox Brasalume</h2><p>Monge 2 · Humano variante</p></div>
            </div>
            <div className={styles.stats}>
              <div><span>PV</span><strong>17/17</strong></div>
              <div><span>CA</span><strong>16</strong></div>
              <div><span>Movimento</span><strong>9 m</strong></div>
              <div><span>Carga</span><strong>33,1 kg</strong></div>
            </div>
            <button className={styles.primary}>Subir de nível</button>
          </article>

          <article className={`${styles.card} ${styles.radarCard}`}>
            <AbilityRadar abilities={abilities} />
          </article>

          <DurabilityCard />
        </div>

        <div className={styles.gridBottom}>
          <article className={styles.card}>
            <div className={styles.cardHeader}><h2>Magias e recursos</h2><span>Ki 2/2</span></div>
            <div className={styles.slotRow}><span /><span /><span className={styles.emptySlot} /><span className={styles.emptySlot} /></div>
            <div className={styles.list}>
              <div><strong>Passo do Vento</strong><small>1 Ki</small></div>
              <div><strong>Defesa Paciente</strong><small>1 Ki</small></div>
              <div><strong>Rajada de Golpes</strong><small>1 Ki</small></div>
            </div>
          </article>

          <MasterGroupCard />

          <article className={styles.card}>
            <div className={styles.cardHeader}><h2>Teia do mestre</h2><span>12 conexões</span></div>
            <div className={styles.graph} aria-label="Prévia da teia de conhecimento">
              <span className={styles.nodeA}>NPCs</span><span className={styles.nodeB}>EVENTOS</span><span className={styles.nodeC}>LOCAIS</span><span className={styles.nodeD}>PISTAS</span>
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
