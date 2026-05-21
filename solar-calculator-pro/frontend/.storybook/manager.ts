import { addons } from '@storybook/manager-api';
import { themes } from '@storybook/theming';

addons.setConfig({
  theme: themes.light,
  panelPosition: 'right',
  sidebar: {
    showRoots: true,
    collapsedRoots: ['other'],
  },
});
