import React, { createContext, useReducer, FC, Dispatch } from 'react';

// Definiere die Typen für deine Anwendungsdaten. Passe diese Schnittstellen
// entsprechend der tatsächlichen Projekt‑ und Ergebnisstruktur an.
export interface ProjectConfiguration {
  moduleQuantity?: number;
  inverterId?: string;
  batteryCapacity?: number;
  // Ergänze weitere Felder nach Bedarf
  [key: string]: any;
}

export interface AnalysisResults {
  [key: string]: number | string | undefined;
}

export interface PricingState {
  baseCost: number;
  discountPercent: number;
  surchargePercent: number;
  finalPrice: number;
}

interface AppState {
  projectData: ProjectConfiguration | null;
  calculationResults: AnalysisResults | null;
  pricing: PricingState;
}

// Aktionen zur Aktualisierung des States
type Action =
  | { type: 'SET_PROJECT_DATA'; payload: ProjectConfiguration }
  | { type: 'SET_CALCULATION_RESULTS'; payload: AnalysisResults }
  | { type: 'UPDATE_PRICING'; payload: Partial<PricingState> };

const initialState: AppState = {
  projectData: null,
  calculationResults: null,
  pricing: {
    baseCost: 0,
    discountPercent: 0,
    surchargePercent: 0,
    finalPrice: 0,
  },
};

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_PROJECT_DATA':
      return { ...state, projectData: action.payload };
    case 'SET_CALCULATION_RESULTS':
      return { ...state, calculationResults: action.payload };
    case 'UPDATE_PRICING':
      return { ...state, pricing: { ...state.pricing, ...action.payload } };
    default:
      return state;
  }
}

export const AppContext = createContext<{ state: AppState; dispatch: Dispatch<Action> }>({
  state: initialState,
  dispatch: () => undefined as any,
});

export const AppProvider: FC<React.PropsWithChildren<{}>> = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
};