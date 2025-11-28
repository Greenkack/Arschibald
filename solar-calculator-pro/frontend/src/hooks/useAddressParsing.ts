/**
 * Address Parsing Hook
 * React hook for address parsing functionality
 */

import { useState, useCallback, useEffect } from 'react';
import { addressParsingService, ParsedAddress, AddressValidationResult } from '../services/addressParsingService';

export interface UseAddressParsingOptions {
  autoParseOnChange?: boolean;
  validateOnChange?: boolean;
  debounceMs?: number;
}

export interface UseAddressParsingReturn {
  parsedAddress: ParsedAddress;
  validationResult: AddressValidationResult | null;
  isLoading: boolean;
  suggestions: string[];
  parseAddress: (address: string) => void;
  validateAddress: (address: Partial<ParsedAddress>) => void;
  clearAddress: () => void;
  formatAddress: () => string;
  getBundeslandFromPLZ: (plz: string) => string | null;
  getBundeslandName: (code: string) => string;
  isGermanAddress: (address: string) => boolean;
}

const emptyAddress: ParsedAddress = {
  street: '', houseNumber: '', postalCode: '', city: '', bundesland: '', isValid: false, confidence: 0
};

export const useAddressParsing = (options: UseAddressParsingOptions = {}): UseAddressParsingReturn => {
  const { autoParseOnChange = true, validateOnChange = true, debounceMs = 300 } = options;
  
  const [parsedAddress, setParsedAddress] = useState<ParsedAddress>(emptyAddress);
  const [validationResult, setValidationResult] = useState<AddressValidationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const parseAddress = useCallback((address: string) => {
    if (!address.trim()) {
      setParsedAddress(emptyAddress);
      setValidationResult(null);
      setSuggestions([]);
      return;
    }
    setIsLoading(true);
    if (debounceTimer) clearTimeout(debounceTimer);
    const timer = setTimeout(() => {
      try {
        const result = addressParsingService.parseAddress(address);
        setParsedAddress(result);
        if (validateOnChange) {
          setValidationResult(addressParsingService.validateAddress(result));
        }
        setSuggestions(addressParsingService.suggestCorrections(address));
      } catch (error) {
        console.error('Address parsing error:', error);
        setParsedAddress(emptyAddress);
        setValidationResult({ isValid: false, errors: ['Fehler beim Parsen'], suggestions: [] });
      } finally {
        setIsLoading(false);
      }
    }, debounceMs);
    setDebounceTimer(timer);
  }, [validateOnChange, debounceMs, debounceTimer]);

  const validateAddress = useCallback((address: Partial<ParsedAddress>) => {
    setValidationResult(addressParsingService.validateAddress(address));
  }, []);

  const clearAddress = useCallback(() => {
    setParsedAddress(emptyAddress);
    setValidationResult(null);
    setSuggestions([]);
    if (debounceTimer) clearTimeout(debounceTimer);
  }, [debounceTimer]);

  const formatAddress = useCallback(() => addressParsingService.formatAddress(parsedAddress), [parsedAddress]);
  const getBundeslandFromPLZ = useCallback((plz: string) => addressParsingService.getBundeslandFromPLZ(plz), []);
  const getBundeslandName = useCallback((code: string) => addressParsingService.getBundeslandName(code), []);
  const isGermanAddress = useCallback((address: string) => addressParsingService.isGermanAddress(address), []);

  useEffect(() => {
    return () => { if (debounceTimer) clearTimeout(debounceTimer); };
  }, [debounceTimer]);

  return {
    parsedAddress, validationResult, isLoading, suggestions,
    parseAddress, validateAddress, clearAddress, formatAddress,
    getBundeslandFromPLZ, getBundeslandName, isGermanAddress
  };
};

export default useAddressParsing;
