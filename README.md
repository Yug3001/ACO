# PathWise
**Interactive Path Planning using Soft Computing Algorithms**

A full-stack academic project implementing four path-planning algorithms with a
real-time interactive web UI. Built for a Soft Computing college project.

---

## Quick Start

### 1. Start the Backend

Open a terminal (cmd or PowerShell) in the `backend/` folder:

```bash
cd backend

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Or just double-click `backend/start.bat`.

The backend runs at: **http://127.0.0.1:8000**
API docs (Swagger UI): **http://127.0.0.1:8000/docs**

---

### 2. Start the Frontend

Open a **second** terminal in the `frontend/` folder:

```bash
cd frontend

# Install Node dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

Or just double-click `frontend/start.bat`.

The frontend runs at: **http://localhost:5173**

Open your browser and go to **http://localhost:5173**.

---

## How to Use the Web UI

### Page 1 — Path Planner

1. Click **Set Start** → click a grid cell to place the start (green)
2. Click **Set Goal** → click a grid cell to place the goal (red)
3. Click **Obstacle** → click/drag cells to draw walls
4. Click **Random** to auto-generate obstacles
5. Select an algorithm: **ACO / GA / PSO / A***
6. Adjust parameters using the sliders
7. Click **Run Algorithm**
8. Watch the path animate on the grid
9. See the result card and convergence graph

### Page 2 — Compare

1. Set up a grid on the Path Planner page
2. Go to **Compare**
3. Click **Run Comparison**
4. All four algorithms run on the same grid
5. View the results table and bar charts
6. Click **[View ACO Path]** etc. to see individual paths

### Page 3 — Analysis

1. Configure experiment parameters with sliders
2. Select number of trials (1–10)
3. Click **Run Experiment**
4. View statistical summary (success rate, avg path length, std dev)
5. View convergence comparison chart across algorithms

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/run` | Run one algorithm |
| POST | `/api/compare` | Run all four algorithms |
| POST | `/api/trials` | Run N trials, return statistics |

### Example request — `/api/run`

```json
{
  "algorithm": "ACO",
  "grid": [["S","E","O"],["E","E","E"],["E","E","F"]],
  "start": [0, 0],
  "goal": [2, 2],
  "allow_diagonal": true,
  "parameters": {
    "ants": 20,
    "iterations": 100,
    "alpha": 1.0,
    "beta": 2.0,
    "evaporation": 0.5,
    "Q": 100
  }
}
```

### Example response

```json
{
  "algorithm": "ACO",
  "success": true,
  "path": [[0,0],[1,1],[2,2]],
  "path_length": 3,
  "execution_time": 0.42,
  "iterations": 100,
  "convergence": [10, 8, 6, 5, 5, ...],
  "pheromone_matrix": [[0.1, 0.5, ...], ...],
  "grid_info": { "rows": 3, "cols": 3, ... }
}
```

---

## Algorithms

| Algorithm | Type | Optimal | Stochastic |
|-----------|------|---------|------------|
| **A\*** | Classical search | Yes (always) | No |
| **ACO** | Swarm intelligence | Approximate | Yes |
| **GA** | Evolutionary | Approximate | Yes |
| **PSO** | Swarm intelligence | Approximate | Yes |

- A* is the **baseline** — it always finds the shortest path
- ACO, GA, PSO are **Soft Computing** methods — results vary per run
- All algorithms use the same 8-directional grid with diagonal support
- All results are **real measured values** — nothing is simulated

---

## Grid Map Format

Maps are text files with space-separated symbols:

| Symbol | Meaning |
|--------|---------|
| `S` | Start cell |
| `F` | Goal (Final) cell |
| `E` | Empty (free) cell |
| `O` | Obstacle |

Example (`maps/map1.txt`):
```
E S E O O
E E E O O
O O E O O
E E E E O
O O E E F
```

---

## Dependencies

**Backend**
- Python 3.8+
- FastAPI
- Uvicorn
- NumPy

**Frontend**
- Node.js 18+
- React 18
- Vite 6
- Recharts 2