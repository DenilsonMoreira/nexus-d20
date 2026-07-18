# Motor de regras

## 1. Princípios

- Funções puras sempre que possível.
- Entradas e saídas serializáveis.
- Versão da regra registrada no evento.
- Sem dependência de interface.
- Cálculos em unidades métricas.
- Overrides do mestre são explícitos.

## 2. Atributos

Modificador de atributo:

```text
floor((pontuação − 10) / 2)
```

O gráfico usa as seis pontuações, mas sempre apresenta alternativa textual.

## 3. Ataque

```text
mod_atk = proficiência_se_aplicável + mod_atributo + bônus_arma + efeitos
total = d20_natural + mod_atk
margem = abs(total - CA)
```

Resultado:

- natural 1: falha crítica;
- natural 20: acerto crítico;
- caso contrário, total >= CA acerta.

Desgaste:

- normal: margem na arma atacante;
- falha crítica: margem × 2 na arma atacante;
- acerto crítico: zero na arma atacante e sugestão margem × 2 em arma, escudo ou armadura do alvo, escolhida pelo mestre.

Resultado exatamente igual à CA gera margem zero por padrão.

## 4. Durabilidade

```text
percentual = atual / máximo × 100
```

Estados:

- 76–100: Ótimo;
- 51–75: Bom;
- 26–50: Regular;
- 11–25: Ruim;
- 0–10: Inutilizável.

Abaixo de 50%, o dado base reduz um passo:

```text
d12 → d10 → d8 → d6 → d4 → 1
```

Em 25% ou menos, erro pode disparar teste de quebra. Em 10% ou menos, não funciona normalmente.

## 5. Materiais

Bases iniciais:

| Material | Pontos-base |
|---|---:|
| Papel/pergaminho | 50 |
| Vidro/cerâmica | 100 |
| Tecido | 180 |
| Osso/chifre | 250 |
| Madeira macia | 300 |
| Couro | 350 |
| Ferro | 400 |
| Madeira rígida | 450 |
| Couro endurecido | 500 |
| Bronze | 550 |
| Aço | 1000 |
| Aço temperado | 1400 |
| Mithral | 1800 |
| Adamantina | 3000 |

```text
durabilidade = base_material × estrutura × qualidade × multiplicador_mágico
```

## 6. Itens mágicos

- Piso automático de 50%.
- Desgaste automático é limitado ao piso.
- Mestre pode autorizar ultrapassagem com motivo.
- Autorreparo por descanso, dia ou condição do item.
- Antimagia pode bloquear o reparo.

Multiplicadores sugeridos:

- magia menor 1,25;
- incomum 1,5;
- raro 2;
- muito raro 3;
- lendário 5;
- artefato sem desgaste automático.

## 7. Visibilidade

Mestre sempre vê valores exatos. Jogador vê percentual se possuir profissão compatível com o domínio do item. Caso contrário, vê somente estado.

Exemplos de domínios:

- metalurgia: armas e armaduras metálicas;
- couro: armaduras, botas e bolsas;
- joalheria: anéis, colares e adornos;
- marcenaria: arcos, cajados e escudos de madeira;
- tecelagem: roupas e tecidos;
- arcano: estruturas mágicas, sem substituir o conhecimento artesanal material.

## 8. Peso

Conversão interna exata da regra 2014:

```text
confortável = Força × 2,26796 kg
muito_sobrecarregado = Força × 4,53592 kg
máximo = Força × 6,80389 kg
empurrar_arrastar_levantar = Força × 13,6078 kg
```

Estados na variante:

- até confortável: sem penalidade;
- acima de confortável: −3 m;
- acima de muito sobrecarregado: −6 m e penalidades da variante;
- acima do máximo: não carrega normalmente.

## 9. Viagem

Interface simplificada:

- rápido: 6 km/h e 48 km/dia;
- normal: 5 km/h e 40 km/dia;
- lento: 3 km/h e 30 km/dia.

Terreno difícil reduz distância pela metade.

Marcha forçada após 8 horas:

```text
CD = 10 + horas além de 8
```

Falha causa um nível de exaustão.

## 10. Fadiga oculta

Módulo homebrew opcional de 0 a 3 pontos. Ao atingir 3, converte em um nível de exaustão e consome 3 pontos.

```text
CD = 8 + ritmo + carga + terreno + clima + recursos + condições − mitigadores
```

Jogador pode receber somente sintomas narrativos.

## 11. Descanso longo

Simulação calcula:

- PV ao máximo;
- recursos marcados como LONG_REST;
- slots conforme progressão;
- metade dos dados de vida, mínimo 1;
- exaustão −1 quando requisitos são satisfeitos;
- fadiga oculta conforme qualidade;
- autorreparo e cargas de itens;
- expiração de condições;
- avanço do relógio.

A aplicação exige token idempotente.

## 12. Preços

```text
preço_final = base × região × raridade × qualidade × reputação
```

Moedas usam Decimal e conversão configurável.

## 13. Overrides

Prioridade:

1. regra específica do personagem;
2. regra da campanha;
3. regra específica da entidade;
4. regra padrão 2014;
5. decisão manual do mestre.
