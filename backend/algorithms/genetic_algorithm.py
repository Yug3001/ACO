# algorithms/genetic_algorithm.py
# --------------------------------
# Genetic Algorithm (GA) for grid-based path planning.
#
# CHROMOSOME REPRESENTATION
# =========================
# Each individual (chromosome) is a list of (row, col) tuples forming a path
# from the Start cell toward the Goal cell.
#
# FITNESS FUNCTION
# ================
# fitness(path) = GOAL_BONUS                 (if goal reached)
#               - path_length                (fewer cells = better)
#               - REVISIT_PENALTY × revisits
#               - OBSTACLE_PENALTY × obstacle_hits
#               - NO_GOAL_PENALTY            (if goal not reached)
#               - 0.5 × heuristic_distance_to_goal_from_last_cell
#
# The heuristic distance term provides a gradient for individuals that don't
# reach the goal yet, steering evolution in the right direction.
#
# GENETIC OPERATORS
# =================
# Selection  : Tournament selection (random subset, keep the fittest).
# Crossover  : Find a cell common to both parents; swap their path suffixes.
# Mutation   : Replace a random suffix with a new random walk.
# Repair     : Remove obstacle hits; deduplicate; extend toward goal.
# Elitism    : Top-N individuals are copied unchanged to the next generation.

import random
import time
from typing import List, Tuple, Optional
from environment.grid import GridEnvironment


# Type alias
Path = List[Tuple[int, int]]

# ------------------------------------------------------------------ #
#  Shared utility functions (also imported by pso.py)                #
# ------------------------------------------------------------------ #

def _random_walk(
    grid:       GridEnvironment,
    start:      Tuple[int, int],
    max_len:    int,
    goal_bias:  float = 0.3
) -> Path:
    """
    Generate a path by random walk from *start*, biased toward the goal.

    Args:
        grid      : Grid environment.
        start     : Starting cell.
        max_len   : Maximum number of cells in the path.
        goal_bias : Probability of greedily picking the neighbour closest
                    to the goal at each step (vs. uniform random choice).

    Returns:
        List of (row, col) tuples.
    """
    path    = [start]
    visited = {start}
    current = start

    for _ in range(max_len - 1):
        if current == grid.goal:
            break
        neighbours = grid.get_neighbors(*current)
        unvisited  = [n for n in neighbours if n not in visited]
        if not unvisited:
            break   # Stuck — no unvisited neighbours

        if random.random() < goal_bias:
            # Greedy: pick neighbour closest to goal
            unvisited.sort(key=lambda n: grid.heuristic(n, grid.goal))
            nxt = unvisited[0]
        else:
            nxt = random.choice(unvisited)

        path.append(nxt)
        visited.add(nxt)
        current = nxt

    return path


def _path_phys_length(path: Path) -> float:
    """
    Physical path length accounting for diagonal moves (cost = √2 ≈ 1.414).
    Cardinal moves cost 1.0.
    """
    total = 0.0
    for i in range(len(path) - 1):
        dr = abs(path[i+1][0] - path[i][0])
        dc = abs(path[i+1][1] - path[i][1])
        total += 1.414 if (dr == 1 and dc == 1) else 1.0
    return total


def _fitness(path: Path, grid: GridEnvironment, max_len: int) -> float:
    """
    Evaluate the fitness of a chromosome (path).

    Returns a scalar — higher is better.
    """
    if not path:
        return -9999.0

    GOAL_BONUS      = 1000.0
    NO_GOAL_PENALTY = 500.0
    REVISIT_PENALTY = 2.0
    OBSTACLE_PENALTY= 100.0

    # Count obstacle hits (should be 0 after repair, but acts as guard)
    obstacle_hits = sum(1 for cell in path if tuple(cell) in grid.obstacles)

    # Count revisited cells
    revisits = len(path) - len(set(tuple(c) for c in path))

    goal_reached = (tuple(path[-1]) == tuple(grid.goal))

    score  = GOAL_BONUS if goal_reached else 0.0
    score -= _path_phys_length(path)               # shorter = better
    score -= REVISIT_PENALTY * revisits
    score -= OBSTACLE_PENALTY * obstacle_hits
    score -= 0.0 if goal_reached else NO_GOAL_PENALTY

    # Partial credit: distance of path end to goal guides non-goal paths
    dist_to_goal = grid.heuristic(tuple(path[-1]), grid.goal)
    score -= 0.5 * dist_to_goal

    return score


def _tournament_select(
    population:     List[Path],
    fitness_scores: List[float],
    k:              int = 3
) -> Path:
    """
    Tournament selection:
    Pick *k* individuals at random and return the one with highest fitness.
    """
    indices   = random.sample(range(len(population)), min(k, len(population)))
    winner_i  = max(indices, key=lambda i: fitness_scores[i])
    return list(population[winner_i])


def _crossover(parent1: Path, parent2: Path, grid: GridEnvironment) -> Tuple[Path, Path]:
    """
    Path crossover operator:

    1. Find cells that appear in both parent paths (excluding start).
    2. Pick one common cell at random.
    3. Swap the path suffixes after that cell.

    Example
    -------
    Parent1: S → A → B → C → G
    Parent2: S → X → B → Y → G
    Common : B
    Child1 : S → A → B → Y → G   (prefix of P1 + suffix of P2)
    Child2 : S → X → B → C → G   (prefix of P2 + suffix of P1)

    If no common cell exists (other than start), return copies of parents.
    """
    p1 = [tuple(c) for c in parent1]
    p2 = [tuple(c) for c in parent2]

    set1   = set(p1)
    set2   = set(p2)
    common = list((set1 & set2) - {tuple(grid.start)})

    if not common:
        return list(p1), list(p2)

    cross_cell = random.choice(common)

    idx1 = next(i for i, c in enumerate(p1) if c == cross_cell)
    idx2 = next(i for i, c in enumerate(p2) if c == cross_cell)

    child1 = list(p1[:idx1 + 1]) + list(p2[idx2 + 1:])
    child2 = list(p2[:idx2 + 1]) + list(p1[idx1 + 1:])

    return child1, child2


def _mutate(
    path:          Path,
    grid:          GridEnvironment,
    mutation_rate: float,
    max_len:       int
) -> Path:
    """
    Mutation operator:

    With probability *mutation_rate*, pick a random split point, keep the
    path prefix, and grow a fresh random walk from that point.
    This introduces diversity while preserving part of the existing path.
    """
    if len(path) <= 2 or random.random() > mutation_rate:
        return path

    split  = random.randint(1, max(1, len(path) - 2))
    prefix = [tuple(c) for c in path[:split]]
    suffix = _random_walk(grid, prefix[-1], max_len - split + 1, goal_bias=0.4)

    # Avoid duplicating the junction cell
    return prefix[:-1] + suffix


def _repair(path: Path, grid: GridEnvironment, max_len: int) -> Path:
    """
    Repair a path produced by crossover or mutation:

    Step 1 — Obstacle removal:
        Truncate path at the first obstacle hit.

    Step 2 — Loop removal:
        Remove cycles (keep first occurrence of each cell).

    Step 3 — Goal extension:
        If goal not yet reached, append a greedy random walk toward the goal.

    Returns a valid (no obstacles, no repeated cells) path starting at start.
    """
    # Step 1 — Truncate at obstacle
    clean: Path = []
    for cell in path:
        c = tuple(cell)
        if not grid.is_valid(*c):
            break
        clean.append(c)

    if not clean:
        clean = [tuple(grid.start)]

    # Step 2 — Deduplicate (remove loops)
    seen:    dict = {}
    deduped: Path = []
    for cell in clean:
        key = tuple(cell)
        if key not in seen:
            seen[key] = len(deduped)
            deduped.append(cell)
        else:
            # Trim back to first occurrence to cut out the loop
            deduped = deduped[:seen[key] + 1]
            seen    = {tuple(deduped[i]): i for i in range(len(deduped))}

    # Step 3 — Extend toward goal if not reached
    if tuple(deduped[-1]) != tuple(grid.goal) and len(deduped) < max_len:
        ext  = _random_walk(grid, deduped[-1],
                             max_len - len(deduped) + 1,
                             goal_bias=0.6)
        full = deduped[:-1] + ext     # avoid duplicating junction

        # Final deduplication
        seen2:  dict = {}
        result: Path = []
        for cell in full:
            key = tuple(cell)
            if key not in seen2:
                seen2[key] = len(result)
                result.append(cell)
        return result

    return deduped


# ------------------------------------------------------------------ #
#  GeneticAlgorithm class                                            #
# ------------------------------------------------------------------ #

class GeneticAlgorithm:
    """
    Genetic Algorithm for grid-based path planning.

    Parameters
    ----------
    grid            : Shared GridEnvironment.
    population_size : Number of chromosomes per generation.
    n_generations   : Number of evolution cycles.
    mutation_rate   : Probability a chromosome is mutated  ∈ [0, 1].
    crossover_rate  : Probability two parents undergo crossover ∈ [0, 1].
    elitism_count   : Number of best individuals carried forward unchanged.
    tournament_size : Contestants per tournament selection round.
    max_path_len    : Upper bound on chromosome length.
    """

    def __init__(
        self,
        grid:            GridEnvironment,
        population_size: int   = 50,
        n_generations:   int   = 100,
        mutation_rate:   float = 0.2,
        crossover_rate:  float = 0.8,
        elitism_count:   int   = 2,
        tournament_size: int   = 3,
        max_path_len:    Optional[int] = None
    ):
        self.grid            = grid
        self.population_size = population_size
        self.n_generations   = n_generations
        self.mutation_rate   = mutation_rate
        self.crossover_rate  = crossover_rate
        self.elitism_count   = elitism_count
        self.tournament_size = tournament_size
        self.max_path_len    = max_path_len or (grid.rows * grid.cols)

    def _init_population(self) -> List[Path]:
        """Seed the initial population with biased random walks."""
        return [
            _random_walk(self.grid, self.grid.start, self.max_path_len, goal_bias=0.4)
            for _ in range(self.population_size)
        ]

    def run(self) -> dict:
        """
        Run the Genetic Algorithm.

        Returns
        -------
        Standard PathWise result dict.
        """
        t_start    = time.time()
        convergence: List[float] = []

        population     = self._init_population()
        fitness_scores = [_fitness(p, self.grid, self.max_path_len) for p in population]

        best_path:   Optional[Path] = None
        best_length: float          = float('inf')

        for gen in range(self.n_generations):
            # Sort population by fitness (descending)
            paired   = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)
            fit_sort = [f for f, _ in paired]
            pop_sort = [p for _, p in paired]

            # Track best goal-reaching individual
            for path in pop_sort:
                if tuple(path[-1]) == tuple(self.grid.goal) and len(path) < best_length:
                    best_length = len(path)
                    best_path   = list(path)

            convergence.append(int(best_length) if best_length < float('inf') else -1)

            # Elitism — carry top individuals forward
            new_pop = [list(p) for p in pop_sort[:self.elitism_count]]

            # Generate offspring
            while len(new_pop) < self.population_size:
                p1 = _tournament_select(population, fitness_scores, self.tournament_size)
                p2 = _tournament_select(population, fitness_scores, self.tournament_size)

                if random.random() < self.crossover_rate:
                    c1, c2 = _crossover(p1, p2, self.grid)
                else:
                    c1, c2 = list(p1), list(p2)

                c1 = _mutate(c1, self.grid, self.mutation_rate, self.max_path_len)
                c2 = _mutate(c2, self.grid, self.mutation_rate, self.max_path_len)
                c1 = _repair(c1, self.grid, self.max_path_len)
                c2 = _repair(c2, self.grid, self.max_path_len)

                new_pop.extend([c1, c2])

            population     = new_pop[:self.population_size]
            fitness_scores = [_fitness(p, self.grid, self.max_path_len) for p in population]

        elapsed = time.time() - t_start
        success = best_path is not None

        return {
            "algorithm":        "GA",
            "success":          success,
            "path":             [list(p) for p in best_path] if success else [],
            "path_length":      int(best_length) if success else -1,
            "execution_time":   round(elapsed, 4),
            "iterations":       self.n_generations,
            "convergence":      convergence,
            "pheromone_matrix": None,
            "grid_info":        self.grid.to_dict()
        }


def run_ga(grid: GridEnvironment, **kwargs) -> dict:
    """
    Run GA on *grid* with optional keyword parameters.

    Keyword args (all optional — defaults shown):
        population_size=50, n_generations=100, mutation_rate=0.2,
        crossover_rate=0.8, elitism_count=2, tournament_size=3

    Returns
    -------
    Standard PathWise result dict.
    """
    return GeneticAlgorithm(grid, **kwargs).run()
