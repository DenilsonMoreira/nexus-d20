type Ability = { label: string; score: number; modifier: number };

type Props = { abilities: Ability[] };

const center = 120;
const radius = 82;

function point(angle: number, value: number): string {
  const normalized = Math.max(0, Math.min(value, 20)) / 20;
  const r = radius * normalized;
  return `${center + Math.cos(angle) * r},${center + Math.sin(angle) * r}`;
}

function modifierLabel(value: number): string {
  return value >= 0 ? `+${value}` : String(value);
}

export function AbilityRadar({ abilities }: Props) {
  const angles = abilities.map((_, index) => -Math.PI / 2 + index * (Math.PI / 3));
  const polygon = abilities.map((ability, index) => point(angles[index], ability.score)).join(" ");
  const outer = angles.map((angle) => point(angle, 20)).join(" ");

  return (
    <section aria-labelledby="ability-title">
      <h2 id="ability-title">Atributos e modificadores</h2>
      <svg viewBox="0 0 240 240" role="img" aria-label="Gráfico hexagonal dos seis atributos" style={{ width: "100%", maxHeight: 240 }}>
        <polygon points={outer} fill="none" stroke="#6d573a" />
        {[5, 10, 15].map((level) => <polygon key={level} points={angles.map((a) => point(a, level)).join(" ")} fill="none" stroke="#332b23" />)}
        {angles.map((angle, index) => <line key={index} x1={center} y1={center} x2={point(angle,20).split(',')[0]} y2={point(angle,20).split(',')[1]} stroke="#3c3329" />)}
        <polygon points={polygon} fill="#bd8e4344" stroke="#d3a65c" strokeWidth="2" />
        {abilities.map((ability, index) => {
          const labelRadius = 105;
          const x = center + Math.cos(angles[index]) * labelRadius;
          const y = center + Math.sin(angles[index]) * labelRadius;
          return <text key={ability.label} x={x} y={y} textAnchor="middle" fill="#dfc79e" fontSize="9">{ability.label}</text>;
        })}
      </svg>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 7 }}>
        {abilities.map((ability) => (
          <div key={ability.label} style={{ background: "#11100f", border: "1px solid #302921", borderRadius: 7, padding: 7, textAlign: "center" }}>
            <small style={{ color: "#93887c", display: "block", fontSize: 9 }}>{ability.label}</small>
            <strong>{ability.score} ({modifierLabel(ability.modifier)})</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
