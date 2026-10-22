# algorithms/pso.py
# -----------------
# Particle Swarm Optimization — discrete path-planning adaptation.
#
# HOW CONTINUOUS PSO MAPS TO DISCRETE PATH PLANNING
# ==================================================
#
#  CONTINUOUS PSO CONCEPT       |  THIS IMPLEMENTATION
#  ─────────────────────────────┼──────────────────────────────────────────────
#  Position  (x_i)              |  Candidate path: list of (row,col) cells
#  Velocity  (v_i)              |  Mutation strength scalar ∈ [0,1]
#  Personal best  (p_best)      |  Best path found by this particle so far
#  Global best    (g_best)      |  Best path found by any particle in the swarm
#  x ← x + v                   |  New path = crossover/mutation of current,
#                               |             p_best and g_best paths
#  v ← w·v + c1·r1·(p-x)       |  v ← clip(w·v + cognitive + social, 0, 1)
#          + c2·r2·(g-x)        |  where cognitive/social terms use PATH SIMILARITY
#
# VELOCITY UPDATE
# ===============
# Velocity represents "how much the particle should change".
# We measure the *difference* between paths using:
#     diff(A, B) = 1 - |cells(A) ∩ cells(B)| / max(|A|, |B|)
#
#     v_new = clip( w·v + c1·r1·diff(path, p_best) + c2·r2·diff(path, g_best), 0, 1 )
#
# Higher velocity → more aggressive mutation in the path update step.
#
# PATH UPDATE
# ===========
# A random number r ∈ [0, c1+c2+1] decides the update type:
#   r < c1        → cognitive move: crossover current path with p_best
#   r < c1+c2     → social move:    crossover current path with g_best
#   otherwise     → inertia:        keep current path
# Then, with probability = particle.velocity, apply a random mutation.
# Finally repair the resulting path (remove obstacles, fill to goal).

import random
import time
import numpy as np
from typing import List, Tuple, Optional
from environment.grid import GridEnvironment
from algorithms.genetic_algorithm import _random_walk, _fitness, _repair, _crossover


Path = List[Tuple[int, int]]


# ------------------------------------------------------------------ #
#  Particle class                                                     #
# ------------------------------------------------------------------ #

class Particle:
    """
    One particle in the PSO swarm.

    Attributes
    ----------
    path          : Current path  (= "position" in PSO terms).
    velocity      : Mutation strength scalar ∈ [0, 1].
    pbest         : Best path found by *this* particle.
    pbest_fitness : Fitness value of pbest.
    """

    def __init__(self, path: Path, velocity: float = 0.5):
        self.path          = [tuple(c) for c in path]
        self.velocity      = velocity
        self.pbest         = list(self.path)
        self.pbest_fitness = float('-inf')

    def update_pbest(self, fitness_fn) -> bool:
        """Update personal best if current path is better. Returns True if improved."""
        current_fitness = fitness_fn(self.path)
        if current_fitness > self.pbest_fitness:
            self.pbest_fitness = current_fitness
            self.pbest         = list(self.path)
            return True
        return False


# ------------------------------------------------------------------ #
#  PSO class                                                         #
# ------------------------------------------------------------------ #

class ParticleSwarmOptimization:
    """
    Discrete PSO adapted for grid path planning.

    Parameters
    ----------
    grid         : Shared GridEnvironment.
    n_particles  : Number of particles (swarm size).
    n_iterations : Number of PSO iterations.
    w            : Inertia weight — controls how much the current mutation
                   strength persists (higher = more inertia = slower change).
    c1           : Cognitive coefficient — attraction to personal best.
    c2           : Social coefficient   — attraction to global best.
    max_path_len : Upper bound on path length.
    """

    def __init__(
        self,
        grid:         GridEnvironment,
        n_particles:  int   = 30,
        n_iterations: int   = 100,
        w:            float = 0.5,
        c1:           float = 1.5,
        c2:           float = 1.5,
        max_path_len: Optional[int] = None
    ):
        self.grid         = grid
        self.n_particles  = n_particles
        self.n_iterations = n_iterations
        self.w            = w
        self.c1           = c1
        self.c2           = c2
        self.max_path_len = max_path_len or (grid.rows * grid.cols)

    def _fitness(self, path: Path) -> float:
        return _fitness(path, self.grid, self.max_path_len)

    def _path_similarity(self, p1: Path, p2: Path) -> float:
        """
        Fraction of cells shared between two paths.
        Ranges from 0.0 (completely different) to 1.0 (identical cell sets).
        Used to estimate how far a particle is from its p_best / g_best.
        """
        s1 = set(tuple(c) for c in p1)
        s2 = set(tuple(c) for c in p2)
        if not s1 or not s2:
            return 0.0
        return len(s1 & s2) / max(len(s1), len(s2))

    def _update_velocity(self, particle: Particle, gbest: Path) -> float:
        """
        Velocity update rule (adapted from standard PSO):

            v_new = w·v + c1·r1·diff(path, p_best) + c2·r2·diff(path, g_best)

        where diff = 1 - similarity.  Clipped to [0, 1].
        """
        r1 = random.random()
        r2 = random.random()

        cognitive = self.c1 * r1 * (1.0 - self._path_similarity(particle.path, particle.pbest))
        social    = self.c2 * r2 * (1.0 - self._path_similarity(particle.path, gbest))

        new_v = self.w * particle.velocity + cognitive + social
        return float(np.clip(new_v, 0.0, 1.0))

    def _update_path(self, particle: Particle, gbest: Path) -> Path:
        """
        Path update rule:

        A random draw decides the update type:
          cognitive (prob ∝ c1) → crossover with p_best
          social    (prob ∝ c2) → crossover with g_best
          inertia               → keep current path

        Then, with probability = velocity, apply a random mutation.
        Finally repair the result.
        """
        new_path = list(particle.path)
        total    = self.c1 + self.c2 + 1.0
        r        = random.random() * total

        if r < self.c1:
            # Cognitive move: crossover with personal best
            child, _ = _crossover(new_path, particle.pbest, self.grid)
            new_path = child
        elif r < self.c1 + self.c2:
            # Social move: crossover with global best
            child, _ = _crossover(new_path, gbest, self.grid)
            new_path = child
        # else: inertia — keep current path

        # Random mutation scaled by velocity
        if random.random() < particle.velocity and len(new_path) > 2:
            split    = random.randint(1, len(new_path) - 1)
            prefix   = [tuple(c) for c in new_path[:split]]
            ext      = _random_walk(self.grid, prefix[-1],
                                     self.max_path_len - split + 1,
                                     goal_bias=0.4)
            new_path = prefix[:-1] + ext

        return _repair(new_path, self.grid, self.max_path_len)

    def run(self) -> dict:
        """
        Execute the PSO algorithm.

        Returns
        -------
        Standard PathWise result dict.
        """
        t_start    = time.time()
        convergence: List[float] = []

        # ---- Initialise swarm ----
        particles = []
        for _ in range(self.n_particles):
            path = _random_walk(self.grid, self.grid.start,
                                 self.max_path_len, goal_bias=0.3)
            path = _repair(path, self.grid, self.max_path_len)
            vel  = random.uniform(0.1, 0.5)
            particles.append(Particle(path, vel))

        # Evaluate initial personal bests
        for p in particles:
            p.update_pbest(self._fitness)

        # Initialise global best  (best by fitness first; prefer goal-reaching)
        gbest:         Path  = list(max(particles, key=lambda p: p.pbest_fitness).pbest)
        gbest_fitness: float = self._fitness(gbest)
        gbest_length:  float = float('inf')

        for p in particles:
            if tuple(p.pbest[-1]) == tuple(self.grid.goal):
                l = len(p.pbest)
                if l < gbest_length:
                    gbest_length = l
                    gbest        = list(p.pbest)
                    gbest_fitness= p.pbest_fitness

        # ---- Main PSO loop ----
        for _ in range(self.n_iterations):
            for particle in particles:
                particle.velocity = self._update_velocity(particle, gbest)
                particle.path     = self._update_path(particle, gbest)

                improved = particle.update_pbest(self._fitness)

                if improved:
                    # Update global best: prefer shorter valid paths
                    if tuple(particle.pbest[-1]) == tuple(self.grid.goal):
                        plen = len(particle.pbest)
                        if plen < gbest_length:
                            gbest_length  = plen
                            gbest         = list(particle.pbest)
                            gbest_fitness = particle.pbest_fitness
                    elif particle.pbest_fitness > gbest_fitness and gbest_length == float('inf'):
                        # No valid path found yet — track best by fitness
                        gbest_fitness = particle.pbest_fitness
                        gbest         = list(particle.pbest)

            convergence.append(int(gbest_length) if gbest_length < float('inf') else -1)

        elapsed = time.time() - t_start
        success = gbest_length < float('inf')

        return {
            "algorithm":        "PSO",
            "success":          success,
            "path":             [list(p) for p in gbest] if success else [],
            "path_length":      int(gbest_length) if success else -1,
            "execution_time":   round(elapsed, 4),
            "iterations":       self.n_iterations,
            "convergence":      convergence,
            "pheromone_matrix": None,
            "grid_info":        self.grid.to_dict()
        }


def run_pso(grid: GridEnvironment, **kwargs) -> dict:
    """
    Run PSO on *grid* with optional keyword parameters.

    Keyword args (all optional — defaults shown):
        n_particles=30, n_iterations=100, w=0.5, c1=1.5, c2=1.5

    Returns
    -------
    Standard PathWise result dict.
    """
    return ParticleSwarmOptimization(grid, **kwargs).run()
