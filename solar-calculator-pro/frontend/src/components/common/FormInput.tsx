import React from 'react';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { MultiSelect } from 'primereact/multiselect';
import { InputTextarea } from 'primereact/inputtextarea';
import { Calendar } from 'primereact/calendar';
import { Checkbox } from 'primereact/checkbox';
import { RadioButton } from 'primereact/radiobutton';
import './FormInput.css';

export interface FormInputProps {
  id?: string;
  name: string;
  label?: string;
  type?: 'text' | 'number' | 'email' | 'password' | 'select' | 'multiselect' | 'textarea' | 'date' | 'checkbox' | 'radio';
  value: any;
  onChange: (value: any) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  helperText?: string;
  options?: Array<{ label: string; value: any }>;
  min?: number;
  max?: number;
  rows?: number;
  className?: string;
}

export const FormInput: React.FC<FormInputProps> = ({
  id,
  name,
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  error,
  helperText,
  options = [],
  min,
  max,
  rows = 3,
  className = '',
}) => {
  const inputId = id || `input-${name}`;
  const hasError = !!error;

  const renderInput = () => {
    switch (type) {
      case 'number':
        return (
          <InputNumber
            id={inputId}
            value={value}
            onValueChange={(e) => onChange(e.value)}
            placeholder={placeholder}
            disabled={disabled}
            min={min}
            max={max}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
          />
        );

      case 'select':
        return (
          <Dropdown
            id={inputId}
            value={value}
            onChange={(e) => onChange(e.value)}
            options={options}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
          />
        );

      case 'multiselect':
        return (
          <MultiSelect
            id={inputId}
            value={value}
            onChange={(e) => onChange(e.value)}
            options={options}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
            display="chip"
          />
        );

      case 'textarea':
        return (
          <InputTextarea
            id={inputId}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            rows={rows}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
          />
        );

      case 'date':
        return (
          <Calendar
            id={inputId}
            value={value}
            onChange={(e) => onChange(e.value)}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
            dateFormat="dd.mm.yy"
          />
        );

      case 'checkbox':
        return (
          <div className="flex align-items-center">
            <Checkbox
              inputId={inputId}
              checked={value}
              onChange={(e) => onChange(e.checked)}
              disabled={disabled}
              className={hasError ? 'p-invalid' : ''}
            />
            {label && (
              <label htmlFor={inputId} className="ml-2 cursor-pointer">
                {label}
                {required && <span className="text-red-500 ml-1">*</span>}
              </label>
            )}
          </div>
        );

      case 'radio':
        return (
          <div className="flex flex-column gap-2">
            {options.map((option) => (
              <div key={option.value} className="flex align-items-center">
                <RadioButton
                  inputId={`${inputId}-${option.value}`}
                  name={name}
                  value={option.value}
                  onChange={(e) => onChange(e.value)}
                  checked={value === option.value}
                  disabled={disabled}
                />
                <label htmlFor={`${inputId}-${option.value}`} className="ml-2 cursor-pointer">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        );

      default:
        return (
          <InputText
            id={inputId}
            type={type}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            className={`w-full ${hasError ? 'p-invalid' : ''}`}
          />
        );
    }
  };

  // For checkbox and radio, label is rendered differently
  if (type === 'checkbox' || type === 'radio') {
    return (
      <div className={`form-input ${className}`}>
        {renderInput()}
        {error && <small className="p-error block mt-1">{error}</small>}
        {helperText && !error && <small className="block mt-1 text-500">{helperText}</small>}
      </div>
    );
  }

  return (
    <div className={`form-input ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block mb-2 font-medium">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      {renderInput()}
      {error && <small className="p-error block mt-1">{error}</small>}
      {helperText && !error && <small className="block mt-1 text-500">{helperText}</small>}
    </div>
  );
};
