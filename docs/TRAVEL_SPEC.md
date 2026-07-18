# Viagem, carga, cansaço e exaustão

## Unidades

- peso: kg;
- combate: m;
- viagem: km;
- líquidos: L.

## Carga variante

O sistema converte internamente a variante de 2014 para kg:

- carga confortável: Força × 2,26796 kg;
- muito sobrecarregado: acima de Força × 4,53592 kg;
- capacidade máxima: Força × 6,80389 kg;
- empurrar, arrastar ou levantar: Força × 13,6078 kg.

Efeitos:

- sobrecarregado: deslocamento −3 m;
- muito sobrecarregado: deslocamento −6 m e demais penalidades da variante;
- acima da capacidade: não transporta normalmente.

## Peso calculado

Somar armas, armaduras, itens equipados, recipientes, conteúdo, munições, moedas, alimento, água e criaturas carregadas. Vestir ou equipar não remove peso.

Cinquenta moedas equivalem internamente a 0,453592 kg. A interface mostra valores arredondados.

## Inventários externos

Carroça, montaria, barco, baú, base e bolsa mágica são locais de inventário. Itens ali armazenados não contam como carga pessoal, salvo regra específica.

## Viagem

Valores simplificados da interface:

| Ritmo | Por hora | Dia de 8 horas |
|---|---:|---:|
| Rápido | 6 km | 48 km |
| Normal | 5 km | 40 km |
| Lento | 3 km | 30 km |

Terreno difícil reduz o progresso pela metade. O personagem mais lento pode limitar o grupo.

## Marcha forçada

Após oito horas, cada hora adicional exige salvaguarda de Constituição:

```text
CD = 10 + horas além de 8
```

Falha causa um nível de exaustão.

## Fadiga oculta

Módulo homebrew opcional de 0 a 3 pontos. Ao atingir 3, converte três pontos em um nível de exaustão.

Fatores de CD:

| Fator | Ajuste |
|---|---:|
| Ritmo lento | −2 |
| Ritmo rápido | +2 |
| Sobrecarregado | +2 |
| Muito sobrecarregado | +4 |
| Terreno difícil | +2 |
| Clima severo | +2 |
| Calor ou frio extremo | +2 |
| Alimentação insuficiente | +2 |
| Água insuficiente | +3 |
| Descanso interrompido | +2 |
| Cada nível de exaustão | +1 |
| Montaria ou veículo adequado | −2 |
| Guia experiente | −1 |
| Equipamento apropriado | −1 |

Base sugerida: CD 8. Falha concede um ponto; falha por 5 ou mais pode conceder dois. O mestre vê o valor exato. O jogador recebe sintomas narrativos.

## Descanso

Descanso longo seguro com alimento e água pode remover dois pontos de fadiga oculta e um nível de exaustão conforme a regra aplicável. Descanso interrompido pode não recuperar fadiga.

## Planejador

O planejador recebe grupo, origem, destino, distância, bioma, ritmo, terreno, clima, montaria, alimento, água e horas. Devolve duração, consumo, personagem limitante, testes e riscos.
