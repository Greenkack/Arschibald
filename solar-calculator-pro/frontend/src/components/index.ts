/**
 * Component Exports
 * 
 * Central export file for all reusable components
 */

// Layout Components (Task 23)
export {
  MainLayout,
  AuthLayout,
  Header,
  Sidebar,
  Footer,
  MobileDrawer,
} from './layout';

// German Input Components (Task 216)
export { GermanNumberInput } from './GermanNumberInput';
export { GermanCurrencyInput } from './GermanCurrencyInput';
export { GermanPercentInput } from './GermanPercentInput';
export { GermanSlider } from './GermanSlider';

// Formatted Display Components (Task 217)
export {
  FormattedNumber,
  FormattedCurrency,
  FormattedPercent,
  FormattedLabel,
  FormattedTableCell,
  FormattedCardValue,
} from './FormattedDisplay';

// Authentication Components (Task 24)
export { PasswordChangeForm } from './PasswordChangeForm';
export { ProtectedRoute } from './ProtectedRoute';
