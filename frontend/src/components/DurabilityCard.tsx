const items = [
  { name: "Espada longa de aço", state: "Ótimo", percent: 82, points: "820/1000" },
  { name: "Armadura de couro", state: "Bom", percent: 64, points: "—" },
  { name: "Bastão simples", state: "Ótimo", percent: 93, points: "—" },
];

export function DurabilityCard() {
  return (
    <article style={{ background: "linear-gradient(145deg,#1c1917,#171513)", border: "1px solid #3b3128", borderRadius: 14, padding: 18 }}>
      <h2 style={{ marginTop: 0, fontFamily: "Georgia,serif", fontWeight: 500 }}>Equipamento</h2>
      <p style={{ color: "#9a8f83", fontSize: 13 }}>Percentual exato depende da profissão do personagem.</p>
      <div style={{ display: "grid", gap: 14 }}>
        {items.map((item) => (
          <div key={item.name}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: 13 }}><strong>{item.name}</strong><span>{item.points}</span></div>
            <div style={{ height: 7, background: "#292520", borderRadius: 999, margin: "8px 0 5px" }}><div style={{ width: `${item.percent}%`, height: "100%", background: item.percent > 75 ? "#76a16f" : "#b38d4d", borderRadius: 999 }} /></div>
            <small style={{ color: "#a4998e" }}>{item.state}</small>
          </div>
        ))}
      </div>
    </article>
  );
}
