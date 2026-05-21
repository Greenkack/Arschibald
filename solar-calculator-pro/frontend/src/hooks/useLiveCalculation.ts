/**
 * useLiveCalculation Hook
 * 
 * React hook for real-time PV system calculations with debouncing.
 * 
 * Requirements: funktionen.txt - "Live-Berechnungen"
 * Task: 252. Live Calculation Engine
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import liveCalculationService, {
  LiveCalculationRequest,
  LiveCalculationResult,
  MonthlyBreakdown,
  RoofOrientation,
  ConsumptionProfile
} from '../services/liveCalculationService';

// ==================== Interfaces ====================

export interface UseLiveCalculationOptions {
  debounceMs?: number;
  autoCalculate?: boolean;
  includeMonthlyBreakdown?: boolean;
}

export interface UseLiveCalculationReturn {
  // Results
  result: LiveCalculationResult | null;
  monthlyBreakdown: MonthlyBreakdown | null;
  
  // State
  loading: boolean;
  error: string | null;
  
  // Input setters
  setModuleCount: (count: number) => void;
  setModulePowerWp: (power: number) => void;
  setRoofOrientation: (orientation: RoofOrientation) => void;
  setRoofAngle: (angle: number) => void;
  setAnnualConsumption: (consumption: number) => void;
  setConsumptionProfile: (profile: ConsumptionProfile) => void;
  setBatteryCapacity: (capacity: number) => void;
  setElectricityPrice: (price: number) => void;
  setFeedInTariff: (tariff: number) => void;
  
  // Current inputs
  inputs: LiveCalculationRequest;
  
  // Actions
  calculate: () => Promise<void>;
  reset: () => void;
  
  // Quick calculations (local, instant)
  quickSystemPower: number;
  quickAnnualYield: number;
}

// ==================== Default Values ====================

const DEFAULT_INPUTS: LiveCalculationRequest = {
  module_count: 20,
  module_power_wp: 400,
  location: 'Deutschland',
  roof_orientation: 'south',
  roof_angle: 30,
  annual_consumption_kwh: 4500,
  consumption_profile: 'standard',
  battery_capacity_kwh: 0,
  battery_efficiency: 0.95,
  electricity_price: 0.35,
  feed_in_tariff: 0.082
};

// ==================== Hook ====================

export function useLiveCalculation(
  initialInputs?: Partial<LiveCalculationRequest>,
  options: UseLiveCalculationOptions = {}
): UseLiveCalculationReturn {
  const {
    debounceMs = 300,
    autoCalculate = true,
    includeMonthlyBreakdown = false
  } = options;

  // State
  const [inputs, setInputs] = useState<LiveCalculationRequest>({
    ...DEFAULT_INPUTS,
    ...initialInputs
  });
  const [result, setResult] = useState<LiveCalculationResult | null>(null);
  const [monthlyBreakdown, setMonthlyBreakdown] = useState<MonthlyBreakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs for debouncing
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const abortController = useRef<AbortController | null>(null);

  // Quick local calculations (instant feedback)
  const quickSystemPower = liveCalculationService.calculateSystemPowerLocal(
    inputs.module_count,
    inputs.module_power_wp || 400
  );

  const orientationFactors: Record<RoofOrientation, number> = {
    south: 1.0,
    south_east: 0.95,
    south_west: 0.95,
    east: 0.85,
    west: 0.85,
    north: 0.55,
    flat: 0.90
  };

  const quickAnnualYield = liveCalculationService.estimateAnnualYieldLocal(
    quickSystemPower,
    orientationFactors[inputs.roof_orientation || 'south']
  );

  // Calculate function
  const calculate = useCallback(async () => {
    // Cancel previous request
    if (abortController.current) {
      abortController.current.abort();
    }
    abortController.current = new AbortController();

    setLoading(true);
    setError(null);

    try {
      const [calcResult, breakdown] = await Promise.all([
        liveCalculationService.calculate(inputs),
        includeMonthlyBreakdown 
          ? liveCalculationService.getMonthlyBreakdown(inputs)
          : Promise.resolve(null)
      ]);

      setResult(calcResult);
      if (breakdown) {
        setMonthlyBreakdown(breakdown);
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setError(err.message || 'Berechnungsfehler');
        console.error('Calculation error:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [inputs, includeMonthlyBreakdown]);

  // Debounced calculation
  useEffect(() => {
    if (!autoCalculate) return;

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(() => {
      calculate();
    }, debounceMs);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [inputs, autoCalculate, debounceMs, calculate]);

  // Input setters
  const setModuleCount = useCallback((count: number) => {
    setInputs(prev => ({ ...prev, module_count: count }));
  }, []);

  const setModulePowerWp = useCallback((power: number) => {
    setInputs(prev => ({ ...prev, module_power_wp: power }));
  }, []);

  const setRoofOrientation = useCallback((orientation: RoofOrientation) => {
    setInputs(prev => ({ ...prev, roof_orientation: orientation }));
  }, []);

  const setRoofAngle = useCallback((angle: number) => {
    setInputs(prev => ({ ...prev, roof_angle: angle }));
  }, []);

  const setAnnualConsumption = useCallback((consumption: number) => {
    setInputs(prev => ({ ...prev, annual_consumption_kwh: consumption }));
  }, []);

  const setConsumptionProfile = useCallback((profile: ConsumptionProfile) => {
    setInputs(prev => ({ ...prev, consumption_profile: profile }));
  }, []);

  const setBatteryCapacity = useCallback((capacity: number) => {
    setInputs(prev => ({ ...prev, battery_capacity_kwh: capacity }));
  }, []);

  const setElectricityPrice = useCallback((price: number) => {
    setInputs(prev => ({ ...prev, electricity_price: price }));
  }, []);

  const setFeedInTariff = useCallback((tariff: number) => {
    setInputs(prev => ({ ...prev, feed_in_tariff: tariff }));
  }, []);

  // Reset function
  const reset = useCallback(() => {
    setInputs({ ...DEFAULT_INPUTS, ...initialInputs });
    setResult(null);
    setMonthlyBreakdown(null);
    setError(null);
  }, [initialInputs]);

  return {
    result,
    monthlyBreakdown,
    loading,
    error,
    setModuleCount,
    setModulePowerWp,
    setRoofOrientation,
    setRoofAngle,
    setAnnualConsumption,
    setConsumptionProfile,
    setBatteryCapacity,
    setElectricityPrice,
    setFeedInTariff,
    inputs,
    calculate,
    reset,
    quickSystemPower,
    quickAnnualYield
  };
}

export default useLiveCalculation;
