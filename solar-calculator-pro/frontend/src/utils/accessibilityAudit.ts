/**
 * Accessibility Audit Utility
 * Provides tools for auditing and testing accessibility compliance
 */

export interface AccessibilityIssue {
  severity: 'error' | 'warning' | 'info';
  type: string;
  element: HTMLElement;
  message: string;
  wcagCriteria?: string;
  suggestion?: string;
}

export interface AccessibilityAuditResult {
  passed: boolean;
  issues: AccessibilityIssue[];
  summary: {
    errors: number;
    warnings: number;
    info: number;
  };
  timestamp: Date;
}

export class AccessibilityAuditor {
  private issues: AccessibilityIssue[] = [];

  /**
   * Run complete accessibility audit
   */
  public audit(container: HTMLElement = document.body): AccessibilityAuditResult {
    this.issues = [];

    // Run all checks
    this.checkImages(container);
    this.checkForms(container);
    this.checkHeadings(container);
    this.checkLinks(container);
    this.checkButtons(container);
    this.checkLandmarks(container);
    this.checkColorContrast(container);
    this.checkKeyboardAccess(container);
    this.checkAriaLabels(container);
    this.checkTabIndex(container);

    // Generate summary
    const summary = {
      errors: this.issues.filter((i) => i.severity === 'error').length,
      warnings: this.issues.filter((i) => i.severity === 'warning').length,
      info: this.issues.filter((i) => i.severity === 'info').length,
    };

    return {
      passed: summary.errors === 0,
      issues: this.issues,
      summary,
      timestamp: new Date(),
    };
  }

  /**
   * Check images for alt text
   */
  private checkImages(container: HTMLElement): void {
    const images = container.querySelectorAll<HTMLImageElement>('img');

    images.forEach((img) => {
      if (!img.hasAttribute('alt')) {
        this.addIssue({
          severity: 'error',
          type: 'missing-alt-text',
          element: img,
          message: 'Image missing alt attribute',
          wcagCriteria: 'WCAG 1.1.1 (Level A)',
          suggestion: 'Add descriptive alt text or alt="" for decorative images',
        });
      } else if (img.alt.trim() === '' && !img.hasAttribute('role')) {
        // Empty alt is OK for decorative images, but should have role="presentation"
        this.addIssue({
          severity: 'info',
          type: 'decorative-image',
          element: img,
          message: 'Image with empty alt should have role="presentation"',
          wcagCriteria: 'WCAG 1.1.1 (Level A)',
          suggestion: 'Add role="presentation" to decorative images',
        });
      }
    });
  }

  /**
   * Check form elements for labels
   */
  private checkForms(container: HTMLElement): void {
    const inputs = container.querySelectorAll<HTMLInputElement>(
      'input:not([type="hidden"]), select, textarea'
    );

    inputs.forEach((input) => {
      const hasLabel =
        input.labels && input.labels.length > 0;
      const hasAriaLabel =
        input.hasAttribute('aria-label') || input.hasAttribute('aria-labelledby');

      if (!hasLabel && !hasAriaLabel) {
        this.addIssue({
          severity: 'error',
          type: 'missing-label',
          element: input,
          message: 'Form input missing label',
          wcagCriteria: 'WCAG 3.3.2 (Level A)',
          suggestion: 'Add a <label> element or aria-label attribute',
        });
      }

      // Check for required fields
      if (input.hasAttribute('required') && !input.hasAttribute('aria-required')) {
        this.addIssue({
          severity: 'warning',
          type: 'missing-aria-required',
          element: input,
          message: 'Required field should have aria-required="true"',
          wcagCriteria: 'WCAG 3.3.2 (Level A)',
          suggestion: 'Add aria-required="true" to required fields',
        });
      }
    });
  }

  /**
   * Check heading hierarchy
   */
  private checkHeadings(container: HTMLElement): void {
    const headings = container.querySelectorAll<HTMLHeadingElement>(
      'h1, h2, h3, h4, h5, h6'
    );

    let previousLevel = 0;

    headings.forEach((heading) => {
      const level = parseInt(heading.tagName.substring(1));

      // Check for skipped levels
      if (previousLevel > 0 && level > previousLevel + 1) {
        this.addIssue({
          severity: 'warning',
          type: 'skipped-heading-level',
          element: heading,
          message: `Heading level skipped from h${previousLevel} to h${level}`,
          wcagCriteria: 'WCAG 1.3.1 (Level A)',
          suggestion: 'Use sequential heading levels',
        });
      }

      previousLevel = level;
    });

    // Check for multiple h1
    const h1Count = container.querySelectorAll('h1').length;
    if (h1Count > 1) {
      this.addIssue({
        severity: 'warning',
        type: 'multiple-h1',
        element: container,
        message: `Page has ${h1Count} h1 elements`,
        wcagCriteria: 'WCAG 1.3.1 (Level A)',
        suggestion: 'Use only one h1 per page',
      });
    }
  }

  /**
   * Check links for accessible names
   */
  private checkLinks(container: HTMLElement): void {
    const links = container.querySelectorAll<HTMLAnchorElement>('a[href]');

    links.forEach((link) => {
      const text = link.textContent?.trim() || '';
      const ariaLabel = link.getAttribute('aria-label');

      if (!text && !ariaLabel) {
        this.addIssue({
          severity: 'error',
          type: 'empty-link',
          element: link,
          message: 'Link has no accessible name',
          wcagCriteria: 'WCAG 2.4.4 (Level A)',
          suggestion: 'Add text content or aria-label to the link',
        });
      }

      // Check for generic link text
      const genericTexts = ['click here', 'read more', 'more', 'here'];
      if (genericTexts.includes(text.toLowerCase())) {
        this.addIssue({
          severity: 'warning',
          type: 'generic-link-text',
          element: link,
          message: 'Link has generic text',
          wcagCriteria: 'WCAG 2.4.4 (Level A)',
          suggestion: 'Use descriptive link text that makes sense out of context',
        });
      }
    });
  }

  /**
   * Check buttons for accessible names
   */
  private checkButtons(container: HTMLElement): void {
    const buttons = container.querySelectorAll<HTMLButtonElement>('button');

    buttons.forEach((button) => {
      const text = button.textContent?.trim() || '';
      const ariaLabel = button.getAttribute('aria-label');

      if (!text && !ariaLabel) {
        this.addIssue({
          severity: 'error',
          type: 'empty-button',
          element: button,
          message: 'Button has no accessible name',
          wcagCriteria: 'WCAG 4.1.2 (Level A)',
          suggestion: 'Add text content or aria-label to the button',
        });
      }
    });
  }

  /**
   * Check for landmark regions
   */
  private checkLandmarks(container: HTMLElement): void {
    const hasMain = container.querySelector('main, [role="main"]');
    const hasNav = container.querySelector('nav, [role="navigation"]');

    if (!hasMain) {
      this.addIssue({
        severity: 'warning',
        type: 'missing-main-landmark',
        element: container,
        message: 'Page missing main landmark',
        wcagCriteria: 'WCAG 1.3.1 (Level A)',
        suggestion: 'Add <main> element or role="main"',
      });
    }

    if (!hasNav) {
      this.addIssue({
        severity: 'info',
        type: 'missing-nav-landmark',
        element: container,
        message: 'Page missing navigation landmark',
        wcagCriteria: 'WCAG 1.3.1 (Level A)',
        suggestion: 'Add <nav> element or role="navigation"',
      });
    }
  }

  /**
   * Check color contrast (simplified)
   */
  private checkColorContrast(container: HTMLElement): void {
    const textElements = container.querySelectorAll<HTMLElement>(
      'p, span, a, button, h1, h2, h3, h4, h5, h6, li, td, th'
    );

    textElements.forEach((element) => {
      const style = window.getComputedStyle(element);
      const fontSize = parseFloat(style.fontSize);
      const fontWeight = style.fontWeight;

      // Large text is 18pt+ or 14pt+ bold
      const isLargeText =
        fontSize >= 24 || (fontSize >= 18.66 && parseInt(fontWeight) >= 700);

      // Simplified check - in production, use a proper contrast calculation library
      const bgColor = style.backgroundColor;
      const textColor = style.color;

      if (bgColor === 'rgba(0, 0, 0, 0)' || textColor === 'rgba(0, 0, 0, 0)') {
        return; // Skip transparent colors
      }

      // This is a placeholder - implement proper contrast ratio calculation
      // Minimum ratio: 4.5:1 for normal text, 3:1 for large text
      this.addIssue({
        severity: 'info',
        type: 'contrast-check',
        element,
        message: 'Color contrast should be verified',
        wcagCriteria: 'WCAG 1.4.3 (Level AA)',
        suggestion: `Ensure ${isLargeText ? '3:1' : '4.5:1'} contrast ratio`,
      });
    });
  }

  /**
   * Check keyboard accessibility
   */
  private checkKeyboardAccess(container: HTMLElement): void {
    const interactiveElements = container.querySelectorAll<HTMLElement>(
      'a, button, input, select, textarea, [onclick], [role="button"]'
    );

    interactiveElements.forEach((element) => {
      const tabIndex = element.getAttribute('tabindex');

      // Check for positive tabindex
      if (tabIndex && parseInt(tabIndex) > 0) {
        this.addIssue({
          severity: 'warning',
          type: 'positive-tabindex',
          element,
          message: 'Positive tabindex disrupts natural tab order',
          wcagCriteria: 'WCAG 2.4.3 (Level A)',
          suggestion: 'Use tabindex="0" or remove tabindex',
        });
      }

      // Check for onclick without keyboard handler
      if (element.hasAttribute('onclick') && element.tagName !== 'BUTTON') {
        const hasKeyHandler =
          element.hasAttribute('onkeydown') || element.hasAttribute('onkeypress');

        if (!hasKeyHandler) {
          this.addIssue({
            severity: 'error',
            type: 'missing-keyboard-handler',
            element,
            message: 'Element with onclick missing keyboard handler',
            wcagCriteria: 'WCAG 2.1.1 (Level A)',
            suggestion: 'Add onKeyDown handler or use <button> element',
          });
        }
      }
    });
  }

  /**
   * Check ARIA labels and roles
   */
  private checkAriaLabels(container: HTMLElement): void {
    const ariaElements = container.querySelectorAll<HTMLElement>('[role]');

    ariaElements.forEach((element) => {
      const role = element.getAttribute('role');

      // Check for invalid roles
      const validRoles = [
        'alert',
        'button',
        'checkbox',
        'dialog',
        'link',
        'navigation',
        'main',
        'region',
        'tab',
        'tabpanel',
        'textbox',
        // Add more valid roles
      ];

      if (role && !validRoles.includes(role)) {
        this.addIssue({
          severity: 'warning',
          type: 'invalid-aria-role',
          element,
          message: `Invalid ARIA role: ${role}`,
          wcagCriteria: 'WCAG 4.1.2 (Level A)',
          suggestion: 'Use a valid ARIA role',
        });
      }
    });
  }

  /**
   * Check tabindex usage
   */
  private checkTabIndex(container: HTMLElement): void {
    const tabIndexElements = container.querySelectorAll<HTMLElement>('[tabindex]');

    tabIndexElements.forEach((element) => {
      const tabIndex = element.getAttribute('tabindex');

      if (tabIndex && parseInt(tabIndex) < -1) {
        this.addIssue({
          severity: 'error',
          type: 'invalid-tabindex',
          element,
          message: `Invalid tabindex value: ${tabIndex}`,
          wcagCriteria: 'WCAG 2.4.3 (Level A)',
          suggestion: 'Use tabindex="0", "-1", or remove tabindex',
        });
      }
    });
  }

  /**
   * Add issue to the list
   */
  private addIssue(issue: AccessibilityIssue): void {
    this.issues.push(issue);
  }

  /**
   * Generate HTML report
   */
  public generateReport(result: AccessibilityAuditResult): string {
    const { summary, issues } = result;

    let html = `
      <div class="accessibility-report">
        <h2>Accessibility Audit Report</h2>
        <p>Generated: ${result.timestamp.toLocaleString()}</p>
        
        <div class="summary">
          <h3>Summary</h3>
          <p>Errors: ${summary.errors}</p>
          <p>Warnings: ${summary.warnings}</p>
          <p>Info: ${summary.info}</p>
          <p>Status: ${result.passed ? 'PASSED' : 'FAILED'}</p>
        </div>

        <div class="issues">
          <h3>Issues</h3>
    `;

    issues.forEach((issue, index) => {
      html += `
        <div class="issue issue-${issue.severity}">
          <h4>${index + 1}. ${issue.type}</h4>
          <p><strong>Severity:</strong> ${issue.severity}</p>
          <p><strong>Message:</strong> ${issue.message}</p>
          ${issue.wcagCriteria ? `<p><strong>WCAG:</strong> ${issue.wcagCriteria}</p>` : ''}
          ${issue.suggestion ? `<p><strong>Suggestion:</strong> ${issue.suggestion}</p>` : ''}
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;

    return html;
  }
}

// Export singleton instance
export const accessibilityAuditor = new AccessibilityAuditor();
