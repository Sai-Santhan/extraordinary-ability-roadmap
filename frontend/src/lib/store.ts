import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  userId: string | null;
  userName: string | null;
  setAuth: (token: string, userId: string, userName: string) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      userId: null,
      userName: null,
      setAuth: (token, userId, userName) => set({ token, userId, userName }),
      clearAuth: () => set({ token: null, userId: null, userName: null }),
      isAuthenticated: () => !!get().token,
    }),
    { name: "auth-storage" }
  )
);

interface AnalysisState {
  currentProfileId: string | null;
  currentStage: string | null;
  stages: Record<string, "pending" | "started" | "completed" | "error">;
  setProfileId: (id: string) => void;
  setStage: (stage: string, status: "pending" | "started" | "completed" | "error") => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>()((set) => ({
  currentProfileId: null,
  currentStage: null,
  stages: {
    ingestion: "pending",
    extraction: "pending",
    assessment: "pending",
    roadmap: "pending",
  },
  setProfileId: (id) => set({ currentProfileId: id }),
  setStage: (stage, status) =>
    set((state) => ({
      currentStage: stage,
      stages: { ...state.stages, [stage]: status },
    })),
  reset: () =>
    set({
      currentProfileId: null,
      currentStage: null,
      stages: {
        ingestion: "pending",
        extraction: "pending",
        assessment: "pending",
        roadmap: "pending",
      },
    }),
}));
