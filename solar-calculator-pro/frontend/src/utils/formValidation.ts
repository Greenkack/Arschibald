/**
 * Form Validation Schemas
 * 
 * Centralized Zod validation schemas for all forms in the application.
 * These schemas provide type-safe validation with German error messages.
 */

import { z } from 'zod';

// Custom error messages in German
const errorMessages = {
  required: 'Dieses Feld ist erforderlich',
  invalidEmail: 'Ungültige E-Mail-Adresse',
  invalidUrl: 'Ungültige URL',
  minLength: (min: number) => `Mindestens ${min} Zeichen erforderlich`,
  maxLength: (max: number) => `Maximal ${max} Zeichen erlaubt`,
  minValue: (min: number) => `Wert muss mindestens ${min} sein`,
  maxValue: (max: number) => `Wert darf maximal ${max} sein`,
  invalidNumber: 'Ungültige Zahl',
  invalidDate: 'Ungültiges Datum',
  passwordMismatch: 'Passwörter stimmen nicht überein',
  weakPassword: 'Passwort muss mindestens 8 Zeichen, einen Großbuchstaben, eine Zahl und ein Sonderzeichen enthalten',
};

// Common field validators
export const validators = {
  email: z.string()
    .min(1, errorMessages.required)
    .email(errorMessages.invalidEmail),
  
  password: z.string()
    .min(8, errorMessages.minLength(8))
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      errorMessages.weakPassword
    ),
  
  url: z.string()
    .url(errorMessages.invalidUrl)
    .optional()
    .or(z.literal('')),
  
  phone: z.string()
    .regex(/^[\d\s\-\+\(\)]+$/, 'Ungültige Telefonnummer')
    .optional()
    .or(z.literal('')),
  
  positiveNumber: z.number({
    required_error: errorMessages.required,
    invalid_type_error: errorMessages.invalidNumber,
  }).positive(errorMessages.minValue(0)),
  
  nonNegativeNumber: z.number({
    required_error: errorMessages.required,
    invalid_type_error: errorMessages.invalidNumber,
  }).nonnegative(errorMessages.minValue(0)),
  
  percentage: z.number({
    required_error: errorMessages.required,
    invalid_type_error: errorMessages.invalidNumber,
  }).min(0, errorMessages.minValue(0)).max(100, errorMessages.maxValue(100)),
  
  requiredString: z.string().min(1, errorMessages.required),
  
  optionalString: z.string().optional().or(z.literal('')),
  
  date: z.date({
    required_error: errorMessages.required,
    invalid_type_error: errorMessages.invalidDate,
  }),
};

// Authentication schemas
export const loginSchema = z.object({
  username: validators.requiredString,
  password: validators.requiredString,
  rememberMe: z.boolean().optional(),
});

export const registerSchema = z.object({
  username: validators.requiredString.min(3, errorMessages.minLength(3)),
  email: validators.email,
  password: validators.password,
  confirmPassword: validators.requiredString,
}).refine((data) => data.password === data.confirmPassword, {
  message: errorMessages.passwordMismatch,
  path: ['confirmPassword'],
});

export const passwordChangeSchema = z.object({
  currentPassword: validators.requiredString,
  newPassword: validators.password,
  confirmPassword: validators.requiredString,
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: errorMessages.passwordMismatch,
  path: ['confirmPassword'],
});

// Solar Calculator schemas
export const solarCalculatorSchema = z.object({
  roofArea: validators.positiveNumber,
  roofType: z.enum(['flat', 'gable', 'hip', 'shed'], {
    required_error: errorMessages.required,
  }),
  roofAngle: z.number()
    .min(0, errorMessages.minValue(0))
    .max(90, errorMessages.maxValue(90)),
  orientation: z.enum(['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest'], {
    required_error: errorMessages.required,
  }),
  moduleType: validators.requiredString,
  annualConsumption: validators.positiveNumber,
  location: validators.requiredString,
  batteryStorage: z.boolean().optional(),
  batteryCapacity: validators.nonNegativeNumber.optional(),
});

// Heat Pump schemas
export const heatPumpSchema = z.object({
  buildingArea: validators.positiveNumber,
  buildingType: z.enum(['single_family', 'multi_family', 'commercial'], {
    required_error: errorMessages.required,
  }),
  insulationLevel: z.enum(['poor', 'average', 'good', 'excellent'], {
    required_error: errorMessages.required,
  }),
  heatingSystem: z.enum(['radiator', 'underfloor', 'mixed'], {
    required_error: errorMessages.required,
  }),
  annualHeatingConsumption: validators.positiveNumber,
  location: validators.requiredString,
  heatPumpType: z.enum(['air_water', 'ground_water', 'water_water'], {
    required_error: errorMessages.required,
  }),
});

// Project schemas
export const projectSchema = z.object({
  name: validators.requiredString.max(100, errorMessages.maxLength(100)),
  customerName: validators.requiredString.max(100, errorMessages.maxLength(100)),
  customerEmail: validators.email.optional().or(z.literal('')),
  customerPhone: validators.phone,
  projectType: z.enum(['solar', 'heatpump', 'combined'], {
    required_error: errorMessages.required,
  }),
  status: z.enum(['draft', 'active', 'completed', 'archived']).optional(),
  notes: validators.optionalString,
});

// Customer schemas (CRM)
export const customerSchema = z.object({
  firstName: validators.requiredString.max(50, errorMessages.maxLength(50)),
  lastName: validators.requiredString.max(50, errorMessages.maxLength(50)),
  email: validators.email,
  phone: validators.phone,
  address: validators.optionalString,
  city: validators.optionalString,
  postalCode: validators.optionalString,
  country: validators.optionalString,
  company: validators.optionalString,
  notes: validators.optionalString,
});

// Product schemas
export const productSchema = z.object({
  name: validators.requiredString.max(200, errorMessages.maxLength(200)),
  category: validators.requiredString,
  manufacturer: validators.requiredString,
  price: validators.nonNegativeNumber,
  description: validators.optionalString,
  specifications: z.record(z.any()).optional(),
  imageUrl: validators.url,
  inStock: z.boolean().optional(),
  sku: validators.optionalString,
});

// Price Matrix schemas
export const priceMatrixUploadSchema = z.object({
  fileName: validators.requiredString,
  matrixType: z.enum(['solar', 'heatpump', 'combined'], {
    required_error: errorMessages.required,
  }),
  description: validators.optionalString,
});

// Settings schemas
export const userSettingsSchema = z.object({
  language: z.enum(['de', 'en']).optional(),
  theme: z.enum(['light', 'dark', 'auto']).optional(),
  notifications: z.boolean().optional(),
  emailNotifications: z.boolean().optional(),
  autoSave: z.boolean().optional(),
  autoSaveInterval: z.number().min(30).max(600).optional(),
});

// Export types for TypeScript
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>;
export type SolarCalculatorFormData = z.infer<typeof solarCalculatorSchema>;
export type HeatPumpFormData = z.infer<typeof heatPumpSchema>;
export type ProjectFormData = z.infer<typeof projectSchema>;
export type CustomerFormData = z.infer<typeof customerSchema>;
export type ProductFormData = z.infer<typeof productSchema>;
export type PriceMatrixUploadFormData = z.infer<typeof priceMatrixUploadSchema>;
export type UserSettingsFormData = z.infer<typeof userSettingsSchema>;
