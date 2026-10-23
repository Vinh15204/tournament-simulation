"""
========================================================================================
🏆 TOURNAMENT MONTE CARLO SIMULATION ENGINE: 8-TEAM ROUND ROBIN + PLAYOFFS
========================================================================================
Tournament Structure:
1. GROUP STAGE:
   - 8 teams compete in a Single Round-Robin (all teams play each other once = 28 matches).
   - Every match is Best-of-3 (Bo3, first to 2 wins: 2-0 or 2-1).
   - Standings & Tie-breakers:
     + 1st Criterion: Match Wins (W-L record)
     + 2nd Criterion: Game Differential (Game Wins minus Game Losses)
     + 3rd Criterion: Head-to-Head result between tied teams
     + 4th Criterion: Initial Elo Rating
2. PLAYOFFS (Knockout Stage):
   - Top 4 teams from the Group Stage qualify for the Single-Elimination Playoffs.
   - Semifinals (Best-of-5 / Bo5):
     + Semifinal 1: Seed #1 vs Seed #4
     + Semifinal 2: Seed #2 vs Seed #3
   - Grand Finals (Best-of-5 / Bo5):
     + Winner of SF1 vs Winner of SF2 -> Champion!
3. DYNAMIC ELO RATING SYSTEM:
   - Ratings dynamically update game-by-game using the international Elo expected score model.
========================================================================================
"""

import os
import sys
import math
import json
import random
import time
from itertools import combinations
from collections import defaultdict
from multiprocessing import Pool, cpu_count

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ======================================================================================
# 1. PARTICIPATING TEAMS & INITIAL ELO RATINGS
# ======================================================================================
TEAMS = {
    'GEN':  {'name': 'Gen.G',               'region': 'LCK', 'elo': 1702.0},
    'HLE':  {'name': 'Hanwha Life Esports', 'region': 'LCK', 'elo': 1623.1},
    'BLG':  {'name': 'Bilibili Gaming',     'region': 'LPL', 'elo': 1599.0},
    'T1':   {'name': 'T1',                  'region': 'LCK', 'elo': 1570.3},
    'DK':   {'name': 'Dplus KIA',           'region': 'LCK', 'elo': 1566.5},
    'AL':   {'name': "Anyone's Legend",     'region': 'LPL', 'elo': 1506.3},
    'G2':   {'name': 'G2 Esports',          'region': 'LEC', 'elo': 1486.9},
    'TL':   {'name': 'Team Liquid',         'region': 'LCS', 'elo': 1469.7},
}

K_FACTOR = 32.0


# ======================================================================================
# 2. ELO FORMULAS & MATCH SIMULATION
# ======================================================================================
def expected_score(rating1, rating2):
    """
    Calculates the expected win probability of team 1 against team 2
    based on the standard logistic Elo formula.
    """
    return 1.0 / (1.0 + 10.0 ** ((rating2 - rating1) / 400.0))

def update_elo(elo1, elo2, score1, score2):
    """
    Calculates post-match Elo adjustments for both teams
    taking into account the final game scores.
    """
    e1 = expected_score(elo1, elo2)
    win_delta = K_FACTOR * (1.0 - e1)
    loss_delta = K_FACTOR * e1
    change = (score1 * win_delta) - (score2 * loss_delta)
    return elo1 + change, elo2 - change

def simulate_series(t1, t2, elos, best_of=3):
    """
    Simulates a Best-of-N series (e.g., Bo3, Bo5).
    Returns: (winner, loser, winner_score, loser_score)
    """
    needed_wins = (best_of + 1) // 2
    s1, s2 = 0, 0
    p1 = expected_score(elos[t1], elos[t2])

    while s1 < needed_wins and s2 < needed_wins:
        if random.random() < p1:
            s1 += 1
        else:
            s2 += 1

    # Dynamically update ratings after the match
    new_e1, new_e2 = update_elo(elos[t1], elos[t2], s1, s2)
    elos[t1] = new_e1
    elos[t2] = new_e2

    if s1 > s2:
        return t1, t2, s1, s2
    return t2, t1, s2, s1


# ======================================================================================
# 3. SINGLE TOURNAMENT RUN (Group Stage -> Knockouts)
# ======================================================================================
def simulate_single_tournament(initial_elos):
    """
    Simulates one complete iteration of the tournament:
    - 28 Single Round-Robin Bo3 matches.
    - Tie-break evaluation.
    - Top 4 Bo5 Semifinals & Grand Finals.
    """
    elos = initial_elos.copy()
    team_codes = list(initial_elos.keys())

    # Group stage record tracking
    match_wins = {t: 0 for t in team_codes}
    match_losses = {t: 0 for t in team_codes}
    game_wins = {t: 0 for t in team_codes}
    game_losses = {t: 0 for t in team_codes}
    head_to_head = {} # (team_a, team_b) -> winner

    # Generate and randomize the 28 match order
    matchups = list(combinations(team_codes, 2))
    random.shuffle(matchups)

    for t1, t2 in matchups:
        w, l, sw, sl = simulate_series(t1, t2, elos, best_of=3)
        match_wins[w] += 1
        match_losses[l] += 1
        game_wins[w] += sw
        game_losses[w] += sl
        game_wins[l] += sl
        game_losses[l] += sw
        head_to_head[(t1, t2)] = w
        head_to_head[(t2, t1)] = w

    # Ranking evaluation:
    # 1. Total Match Wins
    # 2. Game Differential (Wins - Losses)
    # 3. Initial Elo (Fallback)
    def rank_key(team):
        diff = game_wins[team] - game_losses[team]
        return (match_wins[team], diff, initial_elos[team])

    ranked_group = sorted(team_codes, key=rank_key, reverse=True)

    # Head-to-head resolution for two adjacent teams tied in match wins and game differential
    for i in range(len(ranked_group) - 1):
        t_a = ranked_group[i]
        t_b = ranked_group[i + 1]
        diff_a = game_wins[t_a] - game_losses[t_a]
        diff_b = game_wins[t_b] - game_losses[t_b]
        if match_wins[t_a] == match_wins[t_b] and diff_a == diff_b:
            if head_to_head.get((t_a, t_b)) == t_b:
                ranked_group[i], ranked_group[i + 1] = t_b, t_a

    # Record group stage standings (1 through 8)
    group_ranks = {team: idx for idx, team in enumerate(ranked_group, 1)}

    # === PLAYOFFS STAGE (TOP 4 SEEDS) ===
    seed1, seed2, seed3, seed4 = ranked_group[0], ranked_group[1], ranked_group[2], ranked_group[3]

    # Semifinals (Best-of-5):
    # Semifinal 1: Seed 1 vs Seed 4
    sf1_winner, _, _, _ = simulate_series(seed1, seed4, elos, best_of=5)

    # Semifinal 2: Seed 2 vs Seed 3
    sf2_winner, _, _, _ = simulate_series(seed2, seed3, elos, best_of=5)

    # Grand Finals (Best-of-5):
    champion, runner_up, _, _ = simulate_series(sf1_winner, sf2_winner, elos, best_of=5)

    return {
        'group_ranks': group_ranks,
        'top4_teams': [seed1, seed2, seed3, seed4],
        'finalists': [sf1_winner, sf2_winner],
        'champion': champion
    }


# ======================================================================================
# 4. MULTIPROCESSING MONTE CARLO ENGINE
# ======================================================================================
def _worker_task(args):
    """Multiprocessing worker executing a batch of tournament simulations"""
    initial_elos, runs = args
    champ_counts = defaultdict(int)
    final_counts = defaultdict(int)
    top4_counts = defaultdict(int)
    rank_pos_counts = {t: defaultdict(int) for t in initial_elos}
    sum_group_ranks = defaultdict(float)

    for _ in range(runs):
        res = simulate_single_tournament(initial_elos)
        champ_counts[res['champion']] += 1

        for f in res['finalists']:
            final_counts[f] += 1

        for q in res['top4_teams']:
            top4_counts[q] += 1

        for t, rk in res['group_ranks'].items():
            rank_pos_counts[t][rk] += 1
            sum_group_ranks[t] += rk

    return {
        'champ': champ_counts,
        'final': final_counts,
        'top4': top4_counts,
        'rank_pos': rank_pos_counts,
        'sum_ranks': sum_group_ranks,
        'runs': runs
    }

def run_monte_carlo(n_simulations=100000):
    """Runs parallel Monte Carlo simulations and outputs statistical standings"""
    initial_elos = {k: v['elo'] for k, v in TEAMS.items()}
    num_workers = max(1, cpu_count() - 1)
    runs_per_worker = n_simulations // num_workers

    print("=" * 105)
    print(f"🚀 RUNNING MONTE CARLO TOURNAMENT SIMULATION: {n_simulations:,} RUNS")
    print(f"   Format: 8-Team Round Robin (Bo3, 28 Matches) -> Top 4 Knockout Playoffs (Bo5)")
    print(f"   Hardware Acceleration: {num_workers} parallel CPU workers")
    print("=" * 105)

    t0 = time.time()
    tasks = [(initial_elos, runs_per_worker) for _ in range(num_workers)]

    total_champ = defaultdict(int)
    total_final = defaultdict(int)
    total_top4 = defaultdict(int)
    total_rank_pos = {t: defaultdict(int) for t in initial_elos}
    total_sum_ranks = defaultdict(float)
    total_completed = 0

    with Pool(num_workers) as pool:
        for res in pool.imap_unordered(_worker_task, tasks):
            total_completed += res['runs']
            for k, v in res['champ'].items(): total_champ[k] += v
            for k, v in res['final'].items(): total_final[k] += v
            for k, v in res['top4'].items(): total_top4[k] += v
            for t in initial_elos:
                total_sum_ranks[t] += res['sum_ranks'][t]
                for rk, cnt in res['rank_pos'][t].items():
                    total_rank_pos[t][rk] += cnt

    elapsed = time.time() - t0
    rate = total_completed / elapsed if elapsed > 0 else 0
    print(f"✅ Completed {total_completed:,} simulations in {elapsed:.2f}s! ({rate:,.0f} runs/sec)\n")

    # ==================================================================================
    # 5. TABULAR REPORTING & EXPORT
    # ==================================================================================
    ranked_teams = sorted(initial_elos.keys(), key=lambda t: total_champ[t], reverse=True)

    header = f"{'RANK':<5} | {'TEAM':<24} | {'REGION':<8} | {'INITIAL ELO':<11} | {'AVG SEED':<9} | {'TOP 4 (PO)':<11} | {'FINALS':<10} | {'CHAMPION 🏆':<11}"
    sep = "-" * len(header)

    print(sep)
    print("🏆 TOURNAMENT PROBABILITY & ADVANCEMENT BREAKDOWN")
    print(sep)
    print(header)
    print(sep)

    results_export = {}

    for idx, t in enumerate(ranked_teams, 1):
        meta = TEAMS[t]
        name = meta['name']
        region = meta['region']
        elo = meta['elo']
        avg_rank = total_sum_ranks[t] / total_completed
        pct_top4 = (total_top4[t] / total_completed) * 100
        pct_final = (total_final[t] / total_completed) * 100
        pct_champ = (total_champ[t] / total_completed) * 100

        print(f"#{idx:<4} | {name:<24} | {region:<8} | {elo:<11.1f} | #{avg_rank:<8.2f} | {pct_top4:<10.2f}% | {pct_final:<9.2f}% | {pct_champ:<10.2f}%")

        results_export[t] = {
            'rank': idx,
            'name': name,
            'region': region,
            'initial_elo': elo,
            'avg_group_rank': round(avg_rank, 2),
            'top4_rate': round(pct_top4, 2),
            'final_rate': round(pct_final, 2),
            'champion_rate': round(pct_champ, 2),
            'group_rank_distribution': {
                f"Rank_{rk}": round((total_rank_pos[t][rk] / total_completed) * 100, 2)
                for rk in range(1, 9)
            }
        }

    print(sep)
    print("📌 Tie-breakers: Match Wins -> Game Differential -> Head-to-Head -> Elo Rating.\n")
    return results_export


if __name__ == '__main__':
    sims = 100000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        sims = int(sys.argv[1])

    results = run_monte_carlo(n_simulations=sims)

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Full statistical distribution saved to: {out_file}")
