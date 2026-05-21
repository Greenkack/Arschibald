/**
 * Address Parsing Service Tests
 */

import { addressParsingService } from '../services/addressParsingService';

describe('AddressParsingService', () => {
  describe('parseAddress', () => {
    test('should parse standard address with comma', () => {
      const result = addressParsingService.parseAddress('Musterstraße 123, 12345 Berlin');
      expect(result.street).toBe('Musterstraße');
      expect(result.houseNumber).toBe('123');
      expect(result.postalCode).toBe('12345');
      expect(result.city).toBe('Berlin');
      expect(result.bundesland).toBe('BE');
      expect(result.isValid).toBe(true);
    });

    test('should parse address without comma', () => {
      const result = addressParsingService.parseAddress('Hauptstraße 45a 80331 München');
      expect(result.street).toBe('Hauptstraße');
      expect(result.houseNumber).toBe('45a');
      expect(result.postalCode).toBe('80331');
      expect(result.city).toBe('München');
      expect(result.bundesland).toBe('BY');
    });

    test('should return invalid for empty input', () => {
      const result = addressParsingService.parseAddress('');
      expect(result.isValid).toBe(false);
      expect(result.confidence).toBe(0);
    });

    test('should handle addresses with extra spaces', () => {
      const result = addressParsingService.parseAddress('  Musterstraße   123 ,  12345   Berlin  ');
      expect(result.street).toBe('Musterstraße');
      expect(result.isValid).toBe(true);
    });
  });

  describe('getBundeslandFromPLZ', () => {
    test('should return correct Bundesland for Berlin PLZ', () => {
      expect(addressParsingService.getBundeslandFromPLZ('10115')).toBe('BE');
      expect(addressParsingService.getBundeslandFromPLZ('12345')).toBe('BE');
    });

    test('should return correct Bundesland for Bayern PLZ', () => {
      expect(addressParsingService.getBundeslandFromPLZ('80331')).toBe('BY');
      expect(addressParsingService.getBundeslandFromPLZ('90402')).toBe('BY');
    });

    test('should return null for invalid PLZ', () => {
      expect(addressParsingService.getBundeslandFromPLZ('')).toBe(null);
      expect(addressParsingService.getBundeslandFromPLZ('1')).toBe(null);
    });
  });

  describe('validateAddress', () => {
    test('should validate complete address', () => {
      const result = addressParsingService.validateAddress({
        street: 'Musterstraße', houseNumber: '123',
        postalCode: '12345', city: 'Berlin', bundesland: 'BE'
      });
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should detect missing required fields', () => {
      const result = addressParsingService.validateAddress({ houseNumber: '123' });
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Straße ist erforderlich');
      expect(result.errors).toContain('PLZ ist erforderlich');
    });

    test('should detect invalid PLZ format', () => {
      const result = addressParsingService.validateAddress({
        street: 'Musterstraße', postalCode: '123', city: 'Berlin'
      });
      expect(result.errors).toContain('PLZ muss 5 Ziffern haben');
    });
  });

  describe('formatAddress', () => {
    test('should format complete address', () => {
      const formatted = addressParsingService.formatAddress({
        street: 'Musterstraße', houseNumber: '123',
        postalCode: '12345', city: 'Berlin',
        bundesland: 'BE', isValid: true, confidence: 1.0
      });
      expect(formatted).toBe('Musterstraße 123, 12345 Berlin');
    });
  });

  describe('isGermanAddress', () => {
    test('should recognize German addresses', () => {
      expect(addressParsingService.isGermanAddress('Musterstraße 123, 12345 Berlin')).toBe(true);
    });

    test('should reject non-German addresses', () => {
      expect(addressParsingService.isGermanAddress('123 Main Street, New York')).toBe(false);
    });
  });

  describe('getBundeslandName', () => {
    test('should return full Bundesland names', () => {
      expect(addressParsingService.getBundeslandName('BE')).toBe('Berlin');
      expect(addressParsingService.getBundeslandName('BY')).toBe('Bayern');
      expect(addressParsingService.getBundeslandName('NW')).toBe('Nordrhein-Westfalen');
    });
  });
});
