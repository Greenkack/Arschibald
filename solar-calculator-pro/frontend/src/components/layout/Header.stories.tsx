import type { Meta, StoryObj } from '@storybook/react';
import { Header } from './Header';
import { BrowserRouter } from 'react-router-dom';

/**
 * Header is the top navigation component of the application.
 * 
 * ## Features
 * - User menu with profile and logout
 * - Application title/logo
 * - Responsive design
 * - Notification indicators
 * - Quick actions
 * 
 * ## Accessibility
 * - Semantic HTML5 header element
 * - Keyboard navigation
 * - ARIA labels for icon buttons
 * - Focus indicators
 * - Skip to main content link
 */
const meta = {
  title: 'Layout/Header',
  component: Header,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'The main application header with navigation and user menu.',
      },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <BrowserRouter>
        <Story />
      </BrowserRouter>
    ),
  ],
} satisfies Meta<typeof Header>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default header with user logged in
 */
export const Default: Story = {};

/**
 * Header with notifications
 */
export const WithNotifications: Story = {
  args: {
    notificationCount: 3,
  },
};

/**
 * Mobile view
 */
export const Mobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
};
