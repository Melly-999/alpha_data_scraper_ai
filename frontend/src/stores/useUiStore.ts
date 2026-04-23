import { create } from "zustand";

interface UiState {
  selectedSignalId: string | null;
  setSelectedSignalId: (id: string | null) => void;
}

export const useUiStore = create<UiState>((set) => ({
  selectedSignalId: null,
  setSelectedSignalId: (selectedSignalId) => set({ selectedSignalId }),
}));

