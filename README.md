# 🏆 Tournament Monte Carlo Simulation with Dynamic Elo

A high-performance Python Monte Carlo simulation engine for competitive tournaments featuring underlying Elo ratings, dynamic rating updates, round-robin group stages, and single-elimination playoffs.

Designed for esports analysts, tabletop/board game tournament organizers, and competitive gaming researchers.

---

## 🎯 Tournament Format

This simulator models a premier competitive tournament featuring the top 8 teams:

```
[ GROUP STAGE: 8 Teams Single Round-Robin ]
  • 28 Matches (Best-of-3 / Bo3)
  • Tie-breakers: Match Wins ➔ Game Differential ➔ Head-to-Head ➔ Initial Elo
                      │
                      ▼
            [ TOP 4 ADVANCE ]
                      │
     ┌────────────────┴────────────────┐
     ▼                                 ▼
[ SEMIFINAL 1 (Bo5) ]         [ SEMIFINAL 2 (Bo5) ]
  Seed #1 vs Seed #4            Seed #2 vs Seed #3
     │                                 │
     └────────────────┬────────────────┘
                      ▼
             [ GRAND FINALS (Bo5) ]
              Winner SF1 vs Winner SF2
                      │
                      ▼
               🏆 CHAMPION 🏆
```

---

## 📐 Mathematical Formulation

### 1. Elo Win Probability
The probability $P_A$ that Team A wins an individual game against Team B is modeled using the standard logistic Elo curve:

$$P_A = \frac{1}{1 + 10^{(R_B - R_A) / 400}}$$

Where $R_A$ and $R_B$ represent the current Elo ratings of Team A and Team B.

### 2. Dynamic Elo Updates
After every match series, ratings dynamically adjust reflecting actual performance:

$$\Delta R = K \cdot (S_A - E_A)$$

$$\text{New } R_A = R_A + \Delta R$$
$$\text{New } R_B = R_B - \Delta R$$

Where $K = 32$ is the K-factor sensitivity, $E_A$ is expected score, and $S_A$ is the normalized match score.

---

## ⚡ Performance & Parallel Processing

The simulation engine utilizes Python's `multiprocessing` to distribute workload evenly across all available CPU cores:
- **100,000 full tournaments simulated in ~1.8 seconds** (~55,000 tournaments/second on modern multi-core CPUs).
- Fully deterministic probabilistic sampling via `random.random()`.
- Zero external dependencies (runs on pure standard Python library).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher.
- No third-party packages required (`pip install` not needed!).

### Running the Simulation
Clone or download this repository, then execute:

```bash
# Run with default 100,000 simulations
python tournament_sim.py

# Or specify custom number of iterations (e.g., 500,000 or 1,000,000)
python tournament_sim.py 500000
```

---

## 📊 Sample Output

```text
=========================================================================================================
🚀 RUNNING MONTE CARLO TOURNAMENT SIMULATION: 100,000 RUNS
   Format: 8-Team Round Robin (Bo3, 28 Matches) -> Top 4 Knockout Playoffs (Bo5)
   Hardware Acceleration: 11 parallel CPU workers
=========================================================================================================
✅ Completed 99,990 simulations in 1.79s! (55,951 runs/sec)

-----------------------------------------------------------------------------------------------------------
🏆 TOURNAMENT PROBABILITY & ADVANCEMENT BREAKDOWN
-----------------------------------------------------------------------------------------------------------
RANK  | TEAM                     | REGION   | INITIAL ELO | AVG SEED  | TOP 4 (PO)  | FINALS     | CHAMPION 🏆  
-----------------------------------------------------------------------------------------------------------
#1    | Gen.G                    | LCK      | 1702.0      | #2.17     | 90.80     % | 67.27    % | 44.56     %
#2    | Hanwha Life Esports      | LCK      | 1623.1      | #3.40     | 72.45     % | 39.31    % | 18.56     %
#3    | Bilibili Gaming          | LPL      | 1599.0      | #3.85     | 63.88     % | 30.62    % | 13.35     %
#4    | T1                       | LCK      | 1570.3      | #4.38     | 52.95     % | 22.12    % | 8.84      %
#5    | Dplus KIA                | LCK      | 1566.5      | #4.45     | 51.25     % | 21.05    % | 8.27      %
#6    | Anyone's Legend          | LPL      | 1506.3      | #5.60     | 28.37     % | 8.74     % | 2.93      %
#7    | G2 Esports               | LEC      | 1486.9      | #5.94     | 22.37     % | 6.23     % | 2.04      %
#8    | Team Liquid              | LCS      | 1469.7      | #6.22     | 17.95     % | 4.66     % | 1.45      %
-----------------------------------------------------------------------------------------------------------
📌 Tie-breakers: Match Wins -> Game Differential -> Head-to-Head -> Elo Rating.
💾 Full statistical distribution saved to: results.json
```

---

## 🛠️ Customization Guide

### Adapting to Tabletop / Board Games or Custom Leagues
Open `tournament_sim.py` and modify the `TEAMS` dictionary with your custom players or participants:

```python
TEAMS = {
    'P1': {'name': 'Alice',   'region': 'Club A', 'elo': 1750.0},
    'P2': {'name': 'Bob',     'region': 'Club B', 'elo': 1680.0},
    'P3': {'name': 'Charlie', 'region': 'Club A', 'elo': 1610.0},
    'P4': {'name': 'Diana',   'region': 'Club C', 'elo': 1550.0},
    'P5': {'name': 'Ethan',   'region': 'Club B', 'elo': 1500.0},
    'P6': {'name': 'Fiona',   'region': 'Club C', 'elo': 1460.0},
    'P7': {'name': 'George',  'region': 'Club D', 'elo': 1420.0},
    'P8': {'name': 'Hannah',  'region': 'Club D', 'elo': 1380.0},
}
```

### Adjusting Match Series Formats
In `simulate_single_tournament`:
- Change `best_of=3` in the Group Stage to `best_of=1` for single-game round-robins.
- Change `best_of=5` in the Playoffs to `best_of=3` or `best_of=7`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute for any educational, esports, or tabletop gaming project.
