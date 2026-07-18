const characters = [
  { name: "Nox", hp: "8/17", ac: 16, weapon: "Bastão +5", status: "Envenenado" },
  { name: "Seraphina", hp: "14/24", ac: 14, weapon: "Cajado +6", status: "Concentração" },
  { name: "Dorne", hp: "31/38", ac: 18, weapon: "Espada +6", status: "Exaustão 1" },
];

export function MasterGroupCard() {
  return (
    <article style={{ background: "linear-gradient(145deg,#1c1917,#171513)", border: "1px solid #3b3128", borderRadius: 14, padding: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}><h2 style={{ margin: 0, fontFamily: "Georgia,serif", fontWeight: 500 }}>Grupo ativo</h2><span style={{ color: "#b4a181" }}>3 selecionados</span></div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8, margin: "16px 0" }}>
        {characters.map((character) => (
          <label key={character.name} style={{ background: "#11100f", border: "1px solid #302921", borderRadius: 9, padding: 10, display: "grid", gap: 5, fontSize: 12 }}>
            <span><input type="checkbox" defaultChecked /> <strong>{character.name}</strong></span>
            <span>PV {character.hp} · CA {character.ac}</span>
            <span>{character.weapon}</span>
            <small style={{ color: "#b89a70" }}>{character.status}</small>
          </label>
        ))}
      </div>
      <button style={{ width: "100%", padding: 12, border: 0, borderRadius: 8, background: "#9b743d", color: "#130e08", fontWeight: 800 }}>Simular descanso longo</button>
    </article>
  );
}
