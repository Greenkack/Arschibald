/**
 * GermanNumberInput Component Tests
 * 
 * Tests for the GermanNumberInput component with German number formatting.
 * 
 * Requirements: 14.3, 14.6, 14.9
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GermanNumberInput } from '../components/GermanNumberInput';

describe('GermanNumberInput', () => {
  describe('Rendering', () => {
    it('should render with initial value formatted in German', () => {
      render(<GermanNumberInput value={1234.56} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      expect(input.value).toBe('1.234,56');
    });

    it('should render with label', () => {
      render(<GermanNumberInput value={100} onChange={vi.fn()} label="Betrag" />);
      expect(screen.getByText('Betrag')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<GermanNumberInput value={0} onChange={vi.fn()} placeholder="Wert eingeben" />);
      const input = screen.getByPlaceholderText('Wert eingeben');
      expect(input).toBeInTheDocument();
    });

    it('should render with custom decimal places', () => {
      render(<GermanNumberInput value={1234.567} onChange={vi.fn()} decimalPlaces={3} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      expect(input.value).toBe('1.234,567');
    });
  });

  describe('User Input', () => {
    it('should update display value on input', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={0} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      await user.clear(input);
      await user.type(input, '123,45');
      
      expect(input.value).toBe('123,45');
    });

    it('should call onChange with parsed number', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={0} onChange={onChange} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '1.234,56');
      
      expect(onChange).toHaveBeenCalledWith(1234.56);
    });

    it('should allow typing negative numbers', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={0} onChange={onChange} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '-123,45');
      
      expect(onChange).toHaveBeenCalledWith(-123.45);
    });

    it('should allow thousand separators', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={0} onChange={onChange} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '1.234.567,89');
      
      expect(onChange).toHaveBeenCalledWith(1234567.89);
    });
  });

  describe('Validation', () => {
    it('should validate minimum value', async () => {
      const user = userEvent.setup();
      const onValidationError = vi.fn();
      render(
        <GermanNumberInput 
          value={100} 
          onChange={vi.fn()} 
          min={50}
          onValidationError={onValidationError}
        />
      );
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '25,00');
      
      expect(onValidationError).toHaveBeenCalled();
    });

    it('should validate maximum value', async () => {
      const user = userEvent.setup();
      const onValidationError = vi.fn();
      render(
        <GermanNumberInput 
          value={100} 
          onChange={vi.fn()} 
          max={200}
          onValidationError={onValidationError}
        />
      );
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '250,00');
      
      expect(onValidationError).toHaveBeenCalled();
    });

    it('should show error message for invalid format', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={100} onChange={vi.fn()} showError={true} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, 'invalid');
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(screen.getByText(/Ungültiges Zahlenformat/i)).toBeInTheDocument();
      });
    });
  });

  describe('Blur Behavior', () => {
    it('should reformat value on blur', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={0} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      await user.clear(input);
      await user.type(input, '1234.56');
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(input.value).toBe('1.234,56');
      });
    });

    it('should reset to current value on invalid input', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={100} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      await user.clear(input);
      await user.type(input, 'abc');
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(input.value).toBe('100,00');
      });
    });

    it('should clamp to min value on blur', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={100} onChange={onChange} min={50} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '25,00');
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith(50);
      });
    });

    it('should clamp to max value on blur', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={100} onChange={onChange} max={200} />);
      const input = screen.getByRole('textbox');
      
      await user.clear(input);
      await user.type(input, '250,00');
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(onChange).toHaveBeenCalledWith(200);
      });
    });
  });

  describe('Bidirectional Conversion', () => {
    it('should convert from German to number and back', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={0} onChange={onChange} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      // Type German format
      await user.clear(input);
      await user.type(input, '1.234,56');
      
      // Should parse to number
      expect(onChange).toHaveBeenCalledWith(1234.56);
      
      // On blur, should format back to German
      fireEvent.blur(input);
      
      await waitFor(() => {
        expect(input.value).toBe('1.234,56');
      });
    });

    it('should handle round-trip conversion accurately', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      const { rerender } = render(<GermanNumberInput value={1234.56} onChange={onChange} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      // Initial display
      expect(input.value).toBe('1.234,56');
      
      // User edits
      await user.clear(input);
      await user.type(input, '5.678,90');
      fireEvent.blur(input);
      
      // Should update parent
      expect(onChange).toHaveBeenCalledWith(5678.90);
      
      // Rerender with new value
      rerender(<GermanNumberInput value={5678.90} onChange={onChange} />);
      
      // Should display correctly
      expect(input.value).toBe('5.678,90');
    });
  });

  describe('Disabled State', () => {
    it('should not allow input when disabled', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={100} onChange={onChange} disabled={true} />);
      const input = screen.getByRole('textbox');
      
      await user.type(input, '123');
      
      expect(onChange).not.toHaveBeenCalled();
    });

    it('should have disabled styling', () => {
      render(<GermanNumberInput value={100} onChange={vi.fn()} disabled={true} />);
      const input = screen.getByRole('textbox');
      
      expect(input).toBeDisabled();
    });
  });

  describe('Keyboard Input', () => {
    it('should allow only valid characters', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={0} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      await user.clear(input);
      await user.type(input, '123abc,45def');
      
      // Should filter out invalid characters
      expect(input.value).not.toContain('abc');
      expect(input.value).not.toContain('def');
    });

    it('should allow only one decimal separator', async () => {
      const user = userEvent.setup();
      render(<GermanNumberInput value={0} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      await user.clear(input);
      await user.type(input, '123,45,67');
      
      // Should have only one comma
      const commaCount = (input.value.match(/,/g) || []).length;
      expect(commaCount).toBeLessThanOrEqual(1);
    });
  });

  describe('Requirements Compliance', () => {
    it('should meet Requirement 14.3: Apply German formatting to input fields', () => {
      render(<GermanNumberInput value={1234.56} onChange={vi.fn()} />);
      const input = screen.getByRole('textbox') as HTMLInputElement;
      
      // Should display in German format
      expect(input.value).toBe('1.234,56');
      expect(input.value).toContain('.');  // Thousand separator
      expect(input.value).toContain(',');  // Decimal separator
    });

    it('should meet Requirement 14.6: Implement bidirectional conversion', async () => {
      const user = userEvent.setup();
      const onChange = vi.fn();
      render(<GermanNumberInput value={0} onChange={onChange} />);
      const input = screen.getByRole('textbox');
      
      // German format → Number
      await user.clear(input);
      await user.type(input, '1.234,56');
      expect(onChange).toHaveBeenCalledWith(1234.56);
      
      // Number → German format (on blur)
      fireEvent.blur(input);
      await waitFor(() => {
        const inputElement = input as HTMLInputElement;
        expect(inputElement.value).toBe('1.234,56');
      });
    });

    it('should meet Requirement 14.9: Validate German-formatted number inputs', async () => {
      const user = userEvent.setup();
      const onValidationError = vi.fn();
      render(
        <GermanNumberInput 
          value={100} 
          onChange={vi.fn()} 
          min={0}
          max={200}
          onValidationError={onValidationError}
        />
      );
      const input = screen.getByRole('textbox');
      
      // Test validation
      await user.clear(input);
      await user.type(input, '250,00');
      
      expect(onValidationError).toHaveBeenCalled();
    });
  });
});
