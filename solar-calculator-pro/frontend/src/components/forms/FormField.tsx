/**
 * Form Field Components
 * 
 * Reusable form field components integrated with React Hook Form.
 * All components support validation, error display, and German formatting.
 */

import React from 'react';
import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { InputText } from 'primereact/inputtext';
import { InputNumber } from 'primereact/inputnumber';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { MultiSelect } from 'primereact/multiselect';
import { Calendar } from 'primereact/calendar';
import { Checkbox } from 'primereact/checkbox';
import { RadioButton } from 'primereact/radiobutton';
import { Slider } from 'primereact/slider';
import { Password } from 'primereact/password';
import { classNames } from 'primereact/utils';
import './FormField.css';

interface BaseFieldProps<TFieldValues extends FieldValues> {
  name: Path<TFieldValues>;
  control: Control<TFieldValues>;
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  helperText?: string;
  className?: string;
}

/**
 * Text Input Field
 */
export function FormTextField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
}: BaseFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <InputText
            id={field.name}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Number Input Field with German formatting
 */
interface FormNumberFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
  prefix?: string;
  showButtons?: boolean;
  mode?: 'decimal' | 'currency';
  currency?: string;
  minFractionDigits?: number;
  maxFractionDigits?: number;
}

export function FormNumberField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  min,
  max,
  step,
  suffix,
  prefix,
  showButtons = false,
  mode = 'decimal',
  currency = 'EUR',
  minFractionDigits = 2,
  maxFractionDigits = 2,
}: FormNumberFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <InputNumber
            id={field.name}
            value={field.value}
            onValueChange={(e) => field.onChange(e.value)}
            placeholder={placeholder}
            disabled={disabled}
            min={min}
            max={max}
            step={step}
            suffix={suffix}
            prefix={prefix}
            showButtons={showButtons}
            mode={mode}
            currency={currency}
            locale="de-DE"
            minFractionDigits={minFractionDigits}
            maxFractionDigits={maxFractionDigits}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Textarea Field
 */
interface FormTextareaFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  rows?: number;
  autoResize?: boolean;
}

export function FormTextareaField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  rows = 3,
  autoResize = false,
}: FormTextareaFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <InputTextarea
            id={field.name}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            rows={rows}
            autoResize={autoResize}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Dropdown Field
 */
interface FormDropdownFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  options: Array<{ label: string; value: any }>;
  optionLabel?: string;
  optionValue?: string;
  filter?: boolean;
  showClear?: boolean;
}

export function FormDropdownField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  options,
  optionLabel = 'label',
  optionValue = 'value',
  filter = false,
  showClear = false,
}: FormDropdownFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <Dropdown
            id={field.name}
            {...field}
            options={options}
            optionLabel={optionLabel}
            optionValue={optionValue}
            placeholder={placeholder}
            disabled={disabled}
            filter={filter}
            showClear={showClear}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * MultiSelect Field
 */
interface FormMultiSelectFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  options: Array<{ label: string; value: any }>;
  optionLabel?: string;
  optionValue?: string;
  filter?: boolean;
  maxSelectedLabels?: number;
}

export function FormMultiSelectField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  options,
  optionLabel = 'label',
  optionValue = 'value',
  filter = false,
  maxSelectedLabels = 3,
}: FormMultiSelectFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <MultiSelect
            id={field.name}
            {...field}
            options={options}
            optionLabel={optionLabel}
            optionValue={optionValue}
            placeholder={placeholder}
            disabled={disabled}
            filter={filter}
            maxSelectedLabels={maxSelectedLabels}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Date Field
 */
interface FormDateFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  showTime?: boolean;
  showIcon?: boolean;
  dateFormat?: string;
  minDate?: Date;
  maxDate?: Date;
}

export function FormDateField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  showTime = false,
  showIcon = true,
  dateFormat = 'dd.mm.yy',
  minDate,
  maxDate,
}: FormDateFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <Calendar
            id={field.name}
            {...field}
            placeholder={placeholder}
            disabled={disabled}
            showTime={showTime}
            showIcon={showIcon}
            dateFormat={dateFormat}
            minDate={minDate}
            maxDate={maxDate}
            locale="de"
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Checkbox Field
 */
interface FormCheckboxFieldProps<TFieldValues extends FieldValues> extends Omit<BaseFieldProps<TFieldValues>, 'placeholder'> {
  binary?: boolean;
}

export function FormCheckboxField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  disabled,
  helperText,
  className,
  binary = true,
}: FormCheckboxFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field form-field-checkbox', className)}>
          <div className="checkbox-wrapper">
            <Checkbox
              inputId={field.name}
              checked={field.value}
              onChange={(e) => field.onChange(e.checked)}
              disabled={disabled}
              binary={binary}
              className={classNames({ 'p-invalid': fieldState.error })}
            />
            {label && (
              <label htmlFor={field.name} className="checkbox-label">
                {label}
              </label>
            )}
          </div>
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Radio Button Group Field
 */
interface FormRadioFieldProps<TFieldValues extends FieldValues> extends Omit<BaseFieldProps<TFieldValues>, 'placeholder'> {
  options: Array<{ label: string; value: any }>;
}

export function FormRadioField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  disabled,
  required,
  helperText,
  className,
  options,
}: FormRadioFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field form-field-radio', className)}>
          {label && (
            <label className={classNames('radio-group-label', { 'required': required })}>
              {label}
            </label>
          )}
          <div className="radio-group">
            {options.map((option) => (
              <div key={option.value} className="radio-item">
                <RadioButton
                  inputId={`${field.name}-${option.value}`}
                  {...field}
                  value={option.value}
                  checked={field.value === option.value}
                  disabled={disabled}
                  className={classNames({ 'p-invalid': fieldState.error })}
                />
                <label htmlFor={`${field.name}-${option.value}`} className="radio-label">
                  {option.label}
                </label>
              </div>
            ))}
          </div>
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Slider Field
 */
interface FormSliderFieldProps<TFieldValues extends FieldValues> extends Omit<BaseFieldProps<TFieldValues>, 'placeholder'> {
  min?: number;
  max?: number;
  step?: number;
  orientation?: 'horizontal' | 'vertical';
}

export function FormSliderField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  disabled,
  required,
  helperText,
  className,
  min = 0,
  max = 100,
  step = 1,
  orientation = 'horizontal',
}: FormSliderFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field form-field-slider', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label} <span className="slider-value">({field.value})</span>
            </label>
          )}
          <Slider
            id={field.name}
            {...field}
            min={min}
            max={max}
            step={step}
            orientation={orientation}
            disabled={disabled}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}

/**
 * Password Field
 */
interface FormPasswordFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  toggleMask?: boolean;
  feedback?: boolean;
}

export function FormPasswordField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  toggleMask = true,
  feedback = true,
}: FormPasswordFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={classNames('form-field', className)}>
          {label && (
            <label htmlFor={field.name} className={classNames({ 'required': required })}>
              {label}
            </label>
          )}
          <Password
            id={field.name}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            toggleMask={toggleMask}
            feedback={feedback}
            className={classNames({ 'p-invalid': fieldState.error })}
          />
          {fieldState.error && (
            <small className="p-error">{fieldState.error.message}</small>
          )}
          {helperText && !fieldState.error && (
            <small className="p-helper-text">{helperText}</small>
          )}
        </div>
      )}
    />
  );
}
