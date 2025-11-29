/**
 * Task 201: Emoji System Infrastructure
 * =====================================
 * Centralized emoji management service for the entire application.
 */

export interface EmojiMapping {
  key: string;
  emoji: string;
  fallback: string;
  category: EmojiCategory;
  description: string;
}

export type EmojiCategory = 
  | 'navigation'
  | 'actions'
  | 'status'
  | 'energy'
  | 'finance'
  | 'documents'
  | 'alerts'
  | 'misc';

export interface EmojiConfig {
  enabled: boolean;
  useNativeEmoji: boolean;
  fallbackToText: boolean;
  animateOnHover: boolean;
}

// Complete emoji mappings for all UI contexts
export const EMOJI_MAPPINGS: Record<string, EmojiMapping> = {
  // Navigation
  'nav.home': { key: 'nav.home', emoji: '🏠', fallback: 'Home', category: 'navigation', description: 'Home/Dashboard' },
  'nav.projects': { key: 'nav.projects', emoji: '📁', fallback: 'Projects', category: 'navigation', description: 'Projects' },
  'nav.calculator': { key: 'nav.calculator', emoji: '🔢', fallback: 'Calc', category: 'navigation', description: 'Calculator' },
  'nav.solar': { key: 'nav.solar', emoji: '☀️', fallback: 'Solar', category: 'navigation', description: 'Solar Calculator' },
  'nav.heatpump': { key: 'nav.heatpump', emoji: '🔥', fallback: 'Heat', category: 'navigation', description: 'Heat Pump' },
  'nav.crm': { key: 'nav.crm', emoji: '👥', fallback: 'CRM', category: 'navigation', description: 'CRM' },
  'nav.products': { key: 'nav.products', emoji: '📦', fallback: 'Products', category: 'navigation', description: 'Products' },
  'nav.admin': { key: 'nav.admin', emoji: '⚙️', fallback: 'Admin', category: 'navigation', description: 'Admin Panel' },
  'nav.settings': { key: 'nav.settings', emoji: '🔧', fallback: 'Settings', category: 'navigation', description: 'Settings' },
  'nav.help': { key: 'nav.help', emoji: '❓', fallback: 'Help', category: 'navigation', description: 'Help' },
  
  // Actions
  'action.save': { key: 'action.save', emoji: '💾', fallback: 'Save', category: 'actions', description: 'Save' },
  'action.delete': { key: 'action.delete', emoji: '🗑️', fallback: 'Delete', category: 'actions', description: 'Delete' },
  'action.edit': { key: 'action.edit', emoji: '✏️', fallback: 'Edit', category: 'actions', description: 'Edit' },
  'action.add': { key: 'action.add', emoji: '➕', fallback: 'Add', category: 'actions', description: 'Add' },
  'action.remove': { key: 'action.remove', emoji: '➖', fallback: 'Remove', category: 'actions', description: 'Remove' },
  'action.search': { key: 'action.search', emoji: '🔍', fallback: 'Search', category: 'actions', description: 'Search' },
  'action.filter': { key: 'action.filter', emoji: '🔽', fallback: 'Filter', category: 'actions', description: 'Filter' },
  'action.refresh': { key: 'action.refresh', emoji: '🔄', fallback: 'Refresh', category: 'actions', description: 'Refresh' },
  'action.download': { key: 'action.download', emoji: '⬇️', fallback: 'Download', category: 'actions', description: 'Download' },
  'action.upload': { key: 'action.upload', emoji: '⬆️', fallback: 'Upload', category: 'actions', description: 'Upload' },
  'action.export': { key: 'action.export', emoji: '📤', fallback: 'Export', category: 'actions', description: 'Export' },
  'action.import': { key: 'action.import', emoji: '📥', fallback: 'Import', category: 'actions', description: 'Import' },
  'action.print': { key: 'action.print', emoji: '🖨️', fallback: 'Print', category: 'actions', description: 'Print' },
  'action.copy': { key: 'action.copy', emoji: '📋', fallback: 'Copy', category: 'actions', description: 'Copy' },
  'action.share': { key: 'action.share', emoji: '🔗', fallback: 'Share', category: 'actions', description: 'Share' },
  
  // Status
  'status.success': { key: 'status.success', emoji: '✅', fallback: 'OK', category: 'status', description: 'Success' },
  'status.error': { key: 'status.error', emoji: '❌', fallback: 'Error', category: 'status', description: 'Error' },
  'status.warning': { key: 'status.warning', emoji: '⚠️', fallback: 'Warning', category: 'status', description: 'Warning' },
  'status.info': { key: 'status.info', emoji: 'ℹ️', fallback: 'Info', category: 'status', description: 'Info' },
  'status.pending': { key: 'status.pending', emoji: '⏳', fallback: 'Pending', category: 'status', description: 'Pending' },
  'status.loading': { key: 'status.loading', emoji: '⏳', fallback: 'Loading', category: 'status', description: 'Loading' },
  'status.complete': { key: 'status.complete', emoji: '✔️', fallback: 'Done', category: 'status', description: 'Complete' },
  'status.active': { key: 'status.active', emoji: '🟢', fallback: 'Active', category: 'status', description: 'Active' },
  'status.inactive': { key: 'status.inactive', emoji: '🔴', fallback: 'Inactive', category: 'status', description: 'Inactive' },
  
  // Energy
  'energy.solar': { key: 'energy.solar', emoji: '☀️', fallback: 'Solar', category: 'energy', description: 'Solar Energy' },
  'energy.battery': { key: 'energy.battery', emoji: '🔋', fallback: 'Battery', category: 'energy', description: 'Battery' },
  'energy.grid': { key: 'energy.grid', emoji: '🔌', fallback: 'Grid', category: 'energy', description: 'Grid' },
  'energy.consumption': { key: 'energy.consumption', emoji: '💡', fallback: 'Usage', category: 'energy', description: 'Consumption' },
  'energy.production': { key: 'energy.production', emoji: '⚡', fallback: 'Production', category: 'energy', description: 'Production' },
  'energy.savings': { key: 'energy.savings', emoji: '💰', fallback: 'Savings', category: 'energy', description: 'Savings' },
  'energy.co2': { key: 'energy.co2', emoji: '🌱', fallback: 'CO2', category: 'energy', description: 'CO2 Savings' },
  'energy.heatpump': { key: 'energy.heatpump', emoji: '🔥', fallback: 'Heat', category: 'energy', description: 'Heat Pump' },
  
  // Finance
  'finance.euro': { key: 'finance.euro', emoji: '💶', fallback: '€', category: 'finance', description: 'Euro' },
  'finance.price': { key: 'finance.price', emoji: '💰', fallback: 'Price', category: 'finance', description: 'Price' },
  'finance.discount': { key: 'finance.discount', emoji: '🏷️', fallback: 'Discount', category: 'finance', description: 'Discount' },
  'finance.invoice': { key: 'finance.invoice', emoji: '🧾', fallback: 'Invoice', category: 'finance', description: 'Invoice' },
  'finance.chart': { key: 'finance.chart', emoji: '📊', fallback: 'Chart', category: 'finance', description: 'Chart' },
  'finance.trend.up': { key: 'finance.trend.up', emoji: '📈', fallback: '↑', category: 'finance', description: 'Trend Up' },
  'finance.trend.down': { key: 'finance.trend.down', emoji: '📉', fallback: '↓', category: 'finance', description: 'Trend Down' },
  
  // Documents
  'doc.pdf': { key: 'doc.pdf', emoji: '📄', fallback: 'PDF', category: 'documents', description: 'PDF Document' },
  'doc.excel': { key: 'doc.excel', emoji: '📊', fallback: 'Excel', category: 'documents', description: 'Excel File' },
  'doc.image': { key: 'doc.image', emoji: '🖼️', fallback: 'Image', category: 'documents', description: 'Image' },
  'doc.folder': { key: 'doc.folder', emoji: '📁', fallback: 'Folder', category: 'documents', description: 'Folder' },
  'doc.file': { key: 'doc.file', emoji: '📄', fallback: 'File', category: 'documents', description: 'File' },
  
  // Alerts
  'alert.bell': { key: 'alert.bell', emoji: '🔔', fallback: 'Alert', category: 'alerts', description: 'Notification' },
  'alert.urgent': { key: 'alert.urgent', emoji: '🚨', fallback: 'Urgent', category: 'alerts', description: 'Urgent' },
  'alert.new': { key: 'alert.new', emoji: '🆕', fallback: 'New', category: 'alerts', description: 'New' },
  
  // Misc
  'misc.user': { key: 'misc.user', emoji: '👤', fallback: 'User', category: 'misc', description: 'User' },
  'misc.users': { key: 'misc.users', emoji: '👥', fallback: 'Users', category: 'misc', description: 'Users' },
  'misc.calendar': { key: 'misc.calendar', emoji: '📅', fallback: 'Calendar', category: 'misc', description: 'Calendar' },
  'misc.clock': { key: 'misc.clock', emoji: '🕐', fallback: 'Time', category: 'misc', description: 'Time' },
  'misc.location': { key: 'misc.location', emoji: '📍', fallback: 'Location', category: 'misc', description: 'Location' },
  'misc.phone': { key: 'misc.phone', emoji: '📞', fallback: 'Phone', category: 'misc', description: 'Phone' },
  'misc.email': { key: 'misc.email', emoji: '📧', fallback: 'Email', category: 'misc', description: 'Email' },
  'misc.star': { key: 'misc.star', emoji: '⭐', fallback: 'Star', category: 'misc', description: 'Favorite' },
  'misc.heart': { key: 'misc.heart', emoji: '❤️', fallback: 'Heart', category: 'misc', description: 'Like' },
  'misc.lock': { key: 'misc.lock', emoji: '🔒', fallback: 'Lock', category: 'misc', description: 'Locked' },
  'misc.unlock': { key: 'misc.unlock', emoji: '🔓', fallback: 'Unlock', category: 'misc', description: 'Unlocked' },
  'misc.3d': { key: 'misc.3d', emoji: '🎨', fallback: '3D', category: 'misc', description: '3D View' },
  'misc.roof': { key: 'misc.roof', emoji: '🏠', fallback: 'Roof', category: 'misc', description: 'Roof' },
  'misc.module': { key: 'misc.module', emoji: '🔲', fallback: 'Module', category: 'misc', description: 'PV Module' },
};

class EmojiService {
  private config: EmojiConfig = {
    enabled: true,
    useNativeEmoji: true,
    fallbackToText: true,
    animateOnHover: false,
  };

  /**
   * Get emoji by key
   */
  getEmoji(key: string): string {
    if (!this.config.enabled) {
      return this.getFallback(key);
    }
    
    const mapping = EMOJI_MAPPINGS[key];
    if (!mapping) {
      console.warn(`Emoji not found for key: ${key}`);
      return '';
    }
    
    return mapping.emoji;
  }

  /**
   * Get fallback text for emoji
   */
  getFallback(key: string): string {
    const mapping = EMOJI_MAPPINGS[key];
    return mapping?.fallback || '';
  }

  /**
   * Get emoji with fallback
   */
  getEmojiWithFallback(key: string): { emoji: string; fallback: string } {
    const mapping = EMOJI_MAPPINGS[key];
    if (!mapping) {
      return { emoji: '', fallback: '' };
    }
    return {
      emoji: this.config.enabled ? mapping.emoji : '',
      fallback: mapping.fallback,
    };
  }

  /**
   * Get all emojis by category
   */
  getByCategory(category: EmojiCategory): EmojiMapping[] {
    return Object.values(EMOJI_MAPPINGS).filter(m => m.category === category);
  }

  /**
   * Get all categories
   */
  getCategories(): EmojiCategory[] {
    return ['navigation', 'actions', 'status', 'energy', 'finance', 'documents', 'alerts', 'misc'];
  }

  /**
   * Update configuration
   */
  setConfig(config: Partial<EmojiConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current configuration
   */
  getConfig(): EmojiConfig {
    return { ...this.config };
  }

  /**
   * Toggle emoji display
   */
  toggleEmojis(enabled: boolean): void {
    this.config.enabled = enabled;
  }

  /**
   * Check if emojis are enabled
   */
  isEnabled(): boolean {
    return this.config.enabled;
  }

  /**
   * Format text with emoji prefix
   */
  formatWithEmoji(key: string, text: string): string {
    const emoji = this.getEmoji(key);
    return emoji ? `${emoji} ${text}` : text;
  }

  /**
   * Get aria-label for accessibility
   */
  getAriaLabel(key: string): string {
    const mapping = EMOJI_MAPPINGS[key];
    return mapping?.description || mapping?.fallback || '';
  }
}

// Singleton instance
export const emojiService = new EmojiService();

// React hook for emoji service
export function useEmoji(key: string) {
  const emoji = emojiService.getEmoji(key);
  const fallback = emojiService.getFallback(key);
  const ariaLabel = emojiService.getAriaLabel(key);
  
  return {
    emoji,
    fallback,
    ariaLabel,
    formatted: (text: string) => emojiService.formatWithEmoji(key, text),
  };
}

export default emojiService;
