/**
 * Form Field Components - Modern (shadcn/ui)
 * 
 * Reusable form field components integrated with React Hook Form.
 * All components support validation, error display, and German formatting.
 * Migrated from PrimeReact to shadcn/ui.
 */

import { Controller, Control, FieldValues, Path } from 'react-hook-form';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Slider } from '../ui/slider';
import { Label } from '../ui/label';
import { cn } from '@/lib/utils';

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
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <Input
            id={field.name}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            className={cn({ 'border-destructive': fieldState.error })}
          />
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
}: FormNumberFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <div className="relative">
            {prefix && (
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                {prefix}
              </span>
            )}
            <Input
              id={field.name}
              type="number"
              {...field}
              value={field.value ?? ''}
              onChange={(e) => field.onChange(e.target.value === '' ? undefined : parseFloat(e.target.value))}
              placeholder={placeholder}
              disabled={disabled}
              min={min}
              max={max}
              step={step}
              className={cn(
                { 'border-destructive': fieldState.error },
                { 'pl-8': prefix },
                { 'pr-8': suffix },
                'text-right'
              )}
            />
            {suffix && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                {suffix}
              </span>
            )}
          </div>
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
}: FormTextareaFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <Textarea
            id={field.name}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            rows={rows}
            className={cn({ 'border-destructive': fieldState.error })}
          />
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
          )}
        </div>
      )}
    />
  );
}

/**
 * Select (Dropdown) Field
 */
interface FormSelectFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  options: Array<{ label: string; value: string }>;
}

export function FormSelectField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  placeholder,
  disabled,
  required,
  helperText,
  className,
  options,
}: FormSelectFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <Select
            value={field.value}
            onValueChange={field.onChange}
            disabled={disabled}
          >
            <SelectTrigger className={cn({ 'border-destructive': fieldState.error })}>
              <SelectValue placeholder={placeholder} />
            </SelectTrigger>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
          )}
        </div>
      )}
    />
  );
}

/**
 * Multi-Select Field (using multiple checkboxes)
 */
interface FormMultiSelectFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  options: Array<{ label: string; value: string }>;
}

export function FormMultiSelectField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  disabled,
  required,
  helperText,
  className,
  options,
}: FormMultiSelectFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <div className="space-y-2 border rounded-md p-3">
            {options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <Checkbox
                  id={`${field.name}-${option.value}`}
                  checked={(field.value as string[] || []).includes(option.value)}
                  onCheckedChange={(checked) => {
                    const currentValue = (field.value as string[]) || [];
                    if (checked) {
                      field.onChange([...currentValue, option.value]);
                    } else {
                      field.onChange(currentValue.filter((v: string) => v !== option.value));
                    }
                  }}
                  disabled={disabled}
                />
                <Label
                  htmlFor={`${field.name}-${option.value}`}
                  className="text-sm font-normal cursor-pointer"
                >
                  {option.label}
                </Label>
              </div>
            ))}
          </div>
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
          )}
        </div>
      )}
    />
  );
}

/**
 * Date Field (using HTML5 date input)
 */
interface FormDateFieldProps<TFieldValues extends FieldValues> extends BaseFieldProps<TFieldValues> {
  showTime?: boolean;
  minDate?: string;
  maxDate?: string;
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
  minDate,
  maxDate,
}: FormDateFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <Input
            id={field.name}
            type={showTime ? 'datetime-local' : 'date'}
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            min={minDate}
            max={maxDate}
            className={cn({ 'border-destructive': fieldState.error })}
          />
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
  description?: string;
}

export function FormCheckboxField<TFieldValues extends FieldValues>({
  name,
  control,
  label,
  disabled,
  helperText,
  className,
  description,
}: FormCheckboxFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          <div className="flex items-center space-x-2">
            <Checkbox
              id={field.name}
              checked={field.value}
              onCheckedChange={field.onChange}
              disabled={disabled}
              className={cn({ 'border-destructive': fieldState.error })}
            />
            {label && (
              <div className="grid gap-1.5 leading-none">
                <Label
                  htmlFor={field.name}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                >
                  {label}
                </Label>
                {description && (
                  <p className="text-sm text-muted-foreground">{description}</p>
                )}
              </div>
            )}
          </div>
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
  options: Array<{ label: string; value: string; description?: string }>;
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
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <RadioGroup
            value={field.value}
            onValueChange={field.onChange}
            disabled={disabled}
            className="space-y-2"
          >
            {options.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem value={option.value} id={`${field.name}-${option.value}`} />
                <Label
                  htmlFor={`${field.name}-${option.value}`}
                  className="text-sm font-normal cursor-pointer"
                >
                  {option.label}
                  {option.description && (
                    <span className="block text-muted-foreground">{option.description}</span>
                  )}
                </Label>
              </div>
            ))}
          </RadioGroup>
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
}: FormSliderFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-4', className)}>
          {label && (
            <div className="flex items-center justify-between">
              <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
                {label}
              </Label>
              <span className="text-sm font-medium">{field.value ?? min}</span>
            </div>
          )}
          <Slider
            id={field.name}
            value={[field.value ?? min]}
            onValueChange={(vals) => field.onChange(vals[0])}
            min={min}
            max={max}
            step={step}
            disabled={disabled}
            className={cn({ 'opacity-50': fieldState.error })}
          />
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
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
  showToggle?: boolean;
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
}: FormPasswordFieldProps<TFieldValues>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <div className={cn('space-y-2', className)}>
          {label && (
            <Label htmlFor={field.name} className={cn({ 'after:content-["*"] after:ml-0.5 after:text-destructive': required })}>
              {label}
            </Label>
          )}
          <Input
            id={field.name}
            type="password"
            {...field}
            value={field.value || ''}
            placeholder={placeholder}
            disabled={disabled}
            className={cn({ 'border-destructive': fieldState.error })}
          />
          {fieldState.error && (
            <p className="text-sm text-destructive">{fieldState.error.message}</p>
          )}
          {helperText && !fieldState.error && (
            <p className="text-sm text-muted-foreground">{helperText}</p>
          )}
        </div>
      )}
    />
  );
}
