/**
 * Address Auto-Parsing Service
 * 
 * Provides intelligent address parsing for German addresses
 * Supports multiple formats and automatic Bundesland detection
 * Based on funktionen.txt requirement for "automatisches Parsing"
 */

export interface ParsedAddress {
  street: string;
  houseNumber: string;
  postalCode: string;
  city: string;
  bundesland: string;
  isValid: boolean;
  confidence: number;
}

export interface AddressValidationResult {
  isValid: boolean;
  errors: string[];
  suggestions: string[];
}

// PLZ to Bundesland mapping (comprehensive)
const PLZ_TO_BUNDESLAND: { [key: string]: string } = {
  // Baden-Württemberg
  '68': 'BW', '69': 'BW', '70': 'BW', '71': 'BW', '72': 'BW', '73': 'BW', 
  '74': 'BW', '75': 'BW', '76': 'BW', '77': 'BW', '78': 'BW', '79': 'BW',
  '88': 'BW', '89': 'BW',
  // Bayern
  '80': 'BY', '81': 'BY', '82': 'BY', '83': 'BY', '84': 'BY', '85': 'BY',
  '86': 'BY', '87': 'BY', '90': 'BY', '91': 'BY', '92': 'BY', '93': 'BY',
  '94': 'BY', '95': 'BY', '96': 'BY', '97': 'BY',
  // Berlin
  '10': 'BE', '12': 'BE', '13': 'BE',
  // Brandenburg
  '03': 'BB', '14': 'BB', '15': 'BB', '16': 'BB',
  // Bremen
  '28': 'HB',
  // Hamburg
  '20': 'HH', '22': 'HH',
  // Hessen
  '34': 'HE', '35': 'HE', '36': 'HE', '60': 'HE', '61': 'HE', '63': 'HE',
  '64': 'HE', '65': 'HE',
  // Mecklenburg-Vorpommern
  '17': 'MV', '18': 'MV', '19': 'MV',
  // Niedersachsen
  '21': 'NI', '26': 'NI', '27': 'NI', '29': 'NI', '30': 'NI', '31': 'NI',
  '37': 'NI', '38': 'NI', '49': 'NI',
  // Nordrhein-Westfalen
  '32': 'NW', '33': 'NW', '40': 'NW', '41': 'NW', '42': 'NW', '44': 'NW',
  '45': 'NW', '46': 'NW', '47': 'NW', '48': 'NW', '50': 'NW', '51': 'NW',
  '52': 'NW', '53': 'NW', '57': 'NW', '58': 'NW', '59': 'NW',
  // Rheinland-Pfalz
  '54': 'RP', '55': 'RP', '56': 'RP', '67': 'RP',
  // Saarland
  '66': 'SL',
  // Sachsen
  '01': 'SN', '02': 'SN', '04': 'SN', '08': 'SN', '09': 'SN',
  // Sachsen-Anhalt
  '06': 'ST', '39': 'ST',
  // Schleswig-Holstein
  '23': 'SH', '24': 'SH', '25': 'SH',
  // Thüringen
  '07': 'TH', '98': 'TH', '99': 'TH'
};

const BUNDESLAND_NAMES: { [key: string]: string } = {
  'BW': 'Baden-Württemberg',
  'BY': 'Bayern',
  'BE': 'Berlin',
  'BB': 'Brandenburg',
  'HB': 'Bremen',
  'HH': 'Hamburg',
  'HE': 'Hessen',
  'MV': 'Mecklenburg-Vorpommern',
  'NI': 'Niedersachsen',
  'NW': 'Nordrhein-Westfalen',
  'RP': 'Rheinland-Pfalz',
  'SL': 'Saarland',
  'SN': 'Sachsen',
  'ST': 'Sachsen-Anhalt',
  'SH': 'Schleswig-Holstein',
  'TH': 'Thüringen'
};

const STREET_SUFFIXES = [
  'straße', 'str.', 'str', 'gasse', 'weg', 'platz', 'allee', 'ring', 'damm',
  'ufer', 'berg', 'tal', 'höhe', 'park', 'hof', 'markt', 'brücke', 'tor'
];

const ADDRESS_PATTERNS = [
  /^(.+?)\s+(\d+[a-zA-Z]?)\s*,\s*(\d{5})\s+(.+)$/,
  /^(.+?)\s+(\d+[a-zA-Z]?)\s+(\d{5})\s+(.+)$/,
  /^(.+?)\s*,\s*(\d{5})\s+(.+)$/,
  /^(.+?)\s+(\d{5})\s+(.+)$/,
  /^(\d{5})\s+(.+?),\s*(.+?)\s+(\d+[a-zA-Z]?)$/,
  /^(\d{5})\s+(.+?)\s+(.+?)\s+(\d+[a-zA-Z]?)$/
];

class AddressParsingService {
  parseAddress(fullAddress: string): ParsedAddress {
    if (!fullAddress || !fullAddress.trim()) {
      return this.createEmptyResult();
    }
    const cleanAddress = this.cleanAddress(fullAddress);
    for (const pattern of ADDRESS_PATTERNS) {
      const result = this.tryPattern(pattern, cleanAddress);
      if (result.isValid) return result;
    }
    return this.fuzzyParse(cleanAddress);
  }

  validateAddress(address: Partial<ParsedAddress>): AddressValidationResult {
    const errors: string[] = [];
    const suggestions: string[] = [];
    if (!address.street?.trim()) errors.push('Straße ist erforderlich');
    if (!address.postalCode?.trim()) {
      errors.push('PLZ ist erforderlich');
    } else if (!/^\d{5}$/.test(address.postalCode)) {
      errors.push('PLZ muss 5 Ziffern haben');
      suggestions.push('Beispiel: 12345');
    }
    if (!address.city?.trim()) errors.push('Ort ist erforderlich');
    if (address.postalCode && address.bundesland) {
      const expected = this.getBundeslandFromPLZ(address.postalCode);
      if (expected && expected !== address.bundesland) {
        suggestions.push(`PLZ ${address.postalCode} gehört zu ${BUNDESLAND_NAMES[expected]}`);
      }
    }
    return { isValid: errors.length === 0, errors, suggestions };
  }

  getBundeslandFromPLZ(plz: string): string | null {
    if (!plz || plz.length < 2) return null;
    return PLZ_TO_BUNDESLAND[plz.substring(0, 2)] || null;
  }

  getBundeslandName(code: string): string {
    return BUNDESLAND_NAMES[code] || code;
  }

  formatAddress(address: ParsedAddress): string {
    const parts = [];
    if (address.street) {
      parts.push(address.street + (address.houseNumber ? ` ${address.houseNumber}` : ''));
    }
    if (address.postalCode && address.city) {
      parts.push(`${address.postalCode} ${address.city}`);
    }
    return parts.join(', ');
  }

  isGermanAddress(address: string): boolean {
    const plzPattern = /\b\d{5}\b/;
    if (!plzPattern.test(address)) return false;
    const lowerAddress = address.toLowerCase();
    return STREET_SUFFIXES.some(suffix => lowerAddress.includes(suffix));
  }

  suggestCorrections(address: string): string[] {
    const suggestions: string[] = [];
    const corrections: { [key: string]: string } = {
      'strasse': 'straße', 'str ': 'str. ', '  ': ' '
    };
    let corrected = address.toLowerCase();
    for (const [wrong, right] of Object.entries(corrections)) {
      if (corrected.includes(wrong)) {
        corrected = corrected.replace(new RegExp(wrong, 'g'), right);
        suggestions.push(`Meinten Sie: ${corrected}?`);
      }
    }
    return suggestions;
  }

  private createEmptyResult(): ParsedAddress {
    return { street: '', houseNumber: '', postalCode: '', city: '', bundesland: '', isValid: false, confidence: 0 };
  }

  private cleanAddress(address: string): string {
    return address.trim().replace(/\s+/g, ' ').replace(/,\s*,/g, ',').replace(/^,|,$/g, '');
  }

  private tryPattern(pattern: RegExp, address: string): ParsedAddress {
    const match = address.match(pattern);
    if (!match) return this.createEmptyResult();
    let street = '', houseNumber = '', postalCode = '', city = '';
    if (match.length === 5) {
      if (pattern.source.includes('\\d{5}.*,')) {
        [, postalCode, city, street, houseNumber] = match;
      } else {
        [, street, houseNumber, postalCode, city] = match;
      }
    } else if (match.length === 4) {
      if (pattern.source.startsWith('^\\d{5}')) {
        [, postalCode, city, street] = match;
      } else {
        [, street, postalCode, city] = match;
      }
    }
    street = street.trim(); houseNumber = houseNumber.trim();
    postalCode = postalCode.trim(); city = city.trim();
    if (!/^\d{5}$/.test(postalCode)) return this.createEmptyResult();
    const bundesland = this.getBundeslandFromPLZ(postalCode) || '';
    const confidence = this.calculateConfidence(street, houseNumber, postalCode, city);
    return { street, houseNumber, postalCode, city, bundesland, isValid: confidence > 0.5, confidence };
  }

  private fuzzyParse(address: string): ParsedAddress {
    const plzMatch = address.match(/\b(\d{5})\b/);
    if (!plzMatch) return this.createEmptyResult();
    const postalCode = plzMatch[1];
    const plzIndex = address.indexOf(postalCode);
    const afterPLZ = address.substring(plzIndex + 5).trim();
    const cityMatch = afterPLZ.match(/^[^,\d]+/);
    const city = cityMatch ? cityMatch[0].trim() : '';
    const beforePLZ = address.substring(0, plzIndex).trim().replace(/,$/, '');
    const streetMatch = beforePLZ.match(/^(.+?)\s+(\d+[a-zA-Z]?)\s*$/);
    let street = '', houseNumber = '';
    if (streetMatch) { street = streetMatch[1].trim(); houseNumber = streetMatch[2].trim(); }
    else { street = beforePLZ; }
    const bundesland = this.getBundeslandFromPLZ(postalCode) || '';
    const confidence = this.calculateConfidence(street, houseNumber, postalCode, city);
    return { street, houseNumber, postalCode, city, bundesland, isValid: confidence > 0.3, confidence };
  }

  private calculateConfidence(street: string, houseNumber: string, postalCode: string, city: string): number {
    let confidence = 0;
    if (street && street.length > 2) {
      confidence += 0.3;
      if (STREET_SUFFIXES.some(s => street.toLowerCase().includes(s))) confidence += 0.1;
    }
    if (houseNumber && /^\d+[a-zA-Z]?$/.test(houseNumber)) confidence += 0.2;
    if (postalCode && /^\d{5}$/.test(postalCode)) {
      confidence += 0.3;
      if (this.getBundeslandFromPLZ(postalCode)) confidence += 0.1;
    }
    if (city && city.length > 2) confidence += 0.2;
    return Math.min(confidence, 1.0);
  }
}

export const addressParsingService = new AddressParsingService();
export default addressParsingService;
