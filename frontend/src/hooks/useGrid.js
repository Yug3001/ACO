// src/hooks/useGrid.js
import { useState, useCallback } from "react";

const DEFAULT_ROWS = 10;
const DEFAULT_COLS = 10;

function makeEmptyGrid(rows, cols) {
  return Array.from({ length: rows }, () => Array(cols).fill("E"));
}

export function useGrid(initRows = DEFAULT_ROWS, initCols = DEFAULT_COLS) {
  const [rows, setRows] = useState(initRows);
  const [cols, setCols] = useState(initCols);
  const [grid, setGrid] = useState(() => makeEmptyGrid(initRows, initCols));
  const [start, setStart] = useState(null);
  const [goal, setGoal]   = useState(null);

  const resetGrid = useCallback(() => {
    setGrid(makeEmptyGrid(rows, cols));
    setStart(null);
    setGoal(null);
  }, [rows, cols]);

  const resizeGrid = useCallback((newRows, newCols) => {
    setRows(newRows);
    setCols(newCols);
    setGrid(makeEmptyGrid(newRows, newCols));
    setStart(null);
    setGoal(null);
  }, []);

  const setCell = useCallback((r, c, type) => {
    setGrid(prev => {
      const next = prev.map(row => [...row]);
      next[r][c] = type;
      return next;
    });
  }, []);

  const toggleObstacle = useCallback((r, c) => {
    setGrid(prev => {
      const next = prev.map(row => [...row]);
      const isStart = start && start[0] === r && start[1] === c;
      const isGoal  = goal  && goal[0]  === r && goal[1]  === c;
      if (isStart || isGoal) return next;
      next[r][c] = next[r][c] === "O" ? "E" : "O";
      return next;
    });
  }, [start, goal]);

  const placeStart = useCallback((r, c) => {
    setGrid(prev => {
      const next = prev.map(row => [...row]);
      if (next[r][c] === "O") return next;
      if (goal && goal[0] === r && goal[1] === c) return next;
      if (start) next[start[0]][start[1]] = "E";
      next[r][c] = "S";
      return next;
    });
    setStart(prev => {
      if (grid[r][c] === "O") return prev;
      if (goal && goal[0] === r && goal[1] === c) return prev;
      return [r, c];
    });
  }, [start, goal, grid]);

  const placeGoal = useCallback((r, c) => {
    setGrid(prev => {
      const next = prev.map(row => [...row]);
      if (next[r][c] === "O") return next;
      if (start && start[0] === r && start[1] === c) return next;
      if (goal) next[goal[0]][goal[1]] = "E";
      next[r][c] = "F";
      return next;
    });
    setGoal(prev => {
      if (grid[r][c] === "O") return prev;
      if (start && start[0] === r && start[1] === c) return prev;
      return [r, c];
    });
  }, [start, goal, grid]);

  const addRandomObstacles = useCallback((density = 0.25) => {
    setGrid(prev => {
      const next = prev.map((row, r) =>
        row.map((cell, c) => {
          const isStart = start && start[0] === r && start[1] === c;
          const isGoal  = goal  && goal[0]  === r && goal[1]  === c;
          if (isStart || isGoal) return cell;
          return Math.random() < density ? "O" : "E";
        })
      );
      return next;
    });
  }, [start, goal]);

  const clearObstacles = useCallback(() => {
    setGrid(prev =>
      prev.map((row, r) =>
        row.map((cell, c) => {
          if (start && start[0] === r && start[1] === c) return "S";
          if (goal  && goal[0]  === r && goal[1]  === c) return "F";
          return "E";
        })
      )
    );
  }, [start, goal]);

  return {
    rows, cols, grid, start, goal,
    resetGrid, resizeGrid, setCell,
    toggleObstacle, placeStart, placeGoal,
    addRandomObstacles, clearObstacles,
  };
}
