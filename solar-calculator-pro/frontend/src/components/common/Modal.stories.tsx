import type { Meta, StoryObj } from '@storybook/react';
import { Modal } from './Modal';
import { Button } from 'primereact/button';
import { useState } from 'react';

/**
 * Modal is a dialog component for displaying content in an overlay.
 * 
 * ## Features
 * - Customizable header and footer
 * - Close button with callback
 * - Backdrop click to close (optional)
 * - Keyboard ESC to close
 * - Responsive sizing
 * - Smooth animations
 * 
 * ## Accessibility
 * - Focus trap within modal
 * - ESC key to close
 * - Proper ARIA attributes (role="dialog", aria-modal="true")
 * - Focus returns to trigger element on close
 * - Screen reader announcements
 */
const meta = {
  title: 'Common/Modal',
  component: Modal,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A flexible modal dialog component with accessibility features and customizable content.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    visible: {
      control: 'boolean',
      description: 'Controls modal visibility',
    },
    onHide: {
      action: 'closed',
      description: 'Callback fired when modal is closed',
    },
    header: {
      control: 'text',
      description: 'Modal header text or component',
    },
    footer: {
      control: 'text',
      description: 'Modal footer content',
    },
    width: {
      control: 'text',
      description: 'Modal width (CSS value)',
    },
    closable: {
      control: 'boolean',
      description: 'Whether to show close button',
    },
  },
} satisfies Meta<typeof Modal>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Basic modal with header and content
 */
export const Default: Story = {
  args: {
    visible: true,
    header: 'Modal Title',
    children: (
      <div>
        <p>This is the modal content. You can put any React components here.</p>
        <p>The modal will close when you click the X button or press ESC.</p>
      </div>
    ),
  },
};

/**
 * Modal with custom footer
 */
export const WithFooter: Story = {
  args: {
    visible: true,
    header: 'Confirm Action',
    children: <p>Are you sure you want to proceed with this action?</p>,
    footer: (
      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
        <Button label="Cancel" severity="secondary" />
        <Button label="Confirm" severity="danger" />
      </div>
    ),
  },
};

/**
 * Wide modal for forms
 */
export const WideModal: Story = {
  args: {
    visible: true,
    header: 'User Registration Form',
    width: '800px',
    children: (
      <div style={{ padding: '1rem' }}>
        <p>This modal is wider to accommodate form fields.</p>
        <p>Width can be customized using the width prop.</p>
      </div>
    ),
  },
};

/**
 * Modal without close button
 */
export const NoCloseButton: Story = {
  args: {
    visible: true,
    header: 'Important Message',
    closable: false,
    children: (
      <div>
        <p>This modal cannot be closed with the X button.</p>
        <p>You must use the action buttons in the footer.</p>
      </div>
    ),
    footer: (
      <Button label="I Understand" />
    ),
  },
};

/**
 * Interactive example with state
 */
export const Interactive = () => {
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <Button label="Open Modal" onClick={() => setVisible(true)} />
      <Modal
        visible={visible}
        onHide={() => setVisible(false)}
        header="Interactive Modal"
        footer={
          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
            <Button label="Cancel" severity="secondary" onClick={() => setVisible(false)} />
            <Button label="Save" onClick={() => setVisible(false)} />
          </div>
        }
      >
        <p>This modal can be opened and closed interactively.</p>
        <p>Try clicking the buttons or pressing ESC.</p>
      </Modal>
    </div>
  );
};
