import { create } from "zustand";

import type { HealthResponse } from "../types/api";

interface AppMetaState {
  health: HealthResponse | null;
  setHealth: (health: HealthResponse) => void;
}

export const useAppMetaStore = create<AppMetaState>((set) => ({
  health: null,
  setHealth: (health) => set({ health }),
}));

