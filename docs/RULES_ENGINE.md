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

## 3. Progressão

A progressão base usa o nível total do personagem e a tabela do SRD 5.1:

| Nível | XP mínimo | Proficiência |
|---:|---:|---:|
| 1 | 0 | +2 |
| 2 | 300 | +2 |
| 3 | 900 | +2 |
| 4 | 2.700 | +2 |
| 5 | 6.500 | +3 |
| 6 | 14.000 | +3 |
| 7 | 23.000 | +3 |
| 8 | 34.000 | +3 |
| 9 | 48.000 | +4 |
| 10 | 64.000 | +4 |
| 11 | 85.000 | +4 |
| 12 | 100.000 | +4 |
| 13 | 120.000 | +5 |
| 14 | 140.000 | +5 |
| 15 | 165.000 | +5 |
| 16 | 195.000 | +5 |
| 17 | 225.000 | +6 |
| 18 | 265.000 | +6 |
| 19 | 305.000 | +6 |
| 20 | 355.000 | +6 |

O simulador:

- calcula o estado atual e o próximo nível sem persistência;
- informa XP restante e maior nível alcançado pelo XP fornecido;
- avalia um nível por vez, mesmo quando o XP permitir saltos maiores;
- retorna `not_evaluated` sem XP, para não impor progressão por experiência a campanhas por marco;
- retorna `level_cap` no nível 20.

Efeitos de classe, PV, escolhas, magias e multiclasse serão compostos em etapas posteriores antes de existir uma operação de aplicação.

### 3.1. Progressão por classe

As doze classes SRD possuem uma definição determinística de dado de vida, valor fixo de PV e níveis de aumento de atributo:

| Classes | Dado de vida | Valor fixo |
|---|---:|---:|
| Bárbaro | d12 | 7 |
| Guerreiro, Paladino, Patrulheiro | d10 | 6 |
| Bardo, Clérigo, Druida, Monge, Ladino, Bruxo | d8 | 5 |
| Feiticeiro, Mago | d6 | 4 |

O ganho de PV em níveis posteriores é:

```text
ganho = máximo(1, valor fixo ou rolagem informada + modificador de Constituição)
```

O motor não rola dados. Sem método de PV, devolve `hit_points` como escolha pendente. O aumento de atributo é pendente nos níveis 4, 8, 12, 16 e 19 para a maioria das classes; Guerreiro também recebe nos níveis 6 e 14, e Ladino no nível 10.

Esta camada não enumera nem aplica características, subclasses ou magias. Sua resposta é parcial por definição e precisa ser composta com essas regras antes da aplicação da subida de nível.

### 3.2. Aumento de atributos

Quando uma característica de classe concede aumento de atributos, a escolha válida é:

- um atributo recebe `+2`; ou
- dois atributos diferentes recebem `+1` cada.

Esse aumento não pode elevar uma pontuação acima de 20. O simulador devolve pontuações e modificadores antes/depois sem persistência.

Se o modificador de Constituição mudar:

```text
ajuste_PV_máximo = diferença_do_modificador × nível_total_resultante
```

Assim, a mudança considera todos os níveis já alcançados, inclusive o novo. Talentos são uma regra opcional separada e não fazem parte desta simulação.

### 3.3. Escolha de subclasse

O catálogo público contém somente uma subclasse detalhada pelo SRD 5.1 para cada classe:

| Classe | Nível da escolha | Subclasse SRD |
|---|---:|---|
| Bárbaro | 3 | Caminho do Berserker |
| Bardo | 3 | Colégio do Conhecimento |
| Clérigo | 1 | Domínio da Vida |
| Druida | 2 | Círculo da Terra |
| Guerreiro | 3 | Campeão |
| Monge | 3 | Caminho da Mão Aberta |
| Paladino | 3 | Juramento de Devoção |
| Patrulheiro | 3 | Caçador |
| Ladino | 3 | Ladrão |
| Feiticeiro | 1 | Linhagem Dracônica |
| Bruxo | 1 | Patrono Corruptor |
| Mago | 2 | Escola de Evocação |

A simulação informa quando a escolha ainda não está disponível, quando se torna obrigatória e se a seleção pertence à classe. A única opção pública nunca é escolhida automaticamente. Opções privadas ou personalizadas serão compostas separadamente.

## 4. Ataque

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

## 5. Durabilidade

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

## 6. Materiais

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

## 7. Itens mágicos

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

## 8. Visibilidade

Mestre sempre vê valores exatos. Jogador vê percentual se possuir profissão compatível com o domínio do item. Caso contrário, vê somente estado.

Exemplos de domínios:

- metalurgia: armas e armaduras metálicas;
- couro: armaduras, botas e bolsas;
- joalheria: anéis, colares e adornos;
- marcenaria: arcos, cajados e escudos de madeira;
- tecelagem: roupas e tecidos;
- arcano: estruturas mágicas, sem substituir o conhecimento artesanal material.

## 9. Peso

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

## 10. Viagem

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

## 11. Fadiga oculta

Módulo homebrew opcional de 0 a 3 pontos. Ao atingir 3, converte em um nível de exaustão e consome 3 pontos.

```text
CD = 8 + ritmo + carga + terreno + clima + recursos + condições − mitigadores
```

Jogador pode receber somente sintomas narrativos.

## 12. Descanso longo

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

## 13. Preços

```text
preço_final = base × região × raridade × qualidade × reputação
```

Moedas usam Decimal e conversão configurável.

## 14. Overrides

Prioridade:

1. regra específica do personagem;
2. regra da campanha;
3. regra específica da entidade;
4. regra padrão 2014;
5. decisão manual do mestre.
