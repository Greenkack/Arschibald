# Drag and Drop System Guide

## Overview

The Solar Calculator Pro application includes a comprehensive drag and drop system that provides intuitive interaction patterns for file uploads, list reordering, component dragging, and dashboard customization.

## Features

### 1. File Drag and Drop
- Upload files by dragging them into designated drop zones
- Support for multiple file types and size validation
- Visual feedback during drag operations
- Error handling and validation messages

### 2. Component Drag and Drop
- Drag UI components between different zones
- Type-safe drag operations with validation
- Visual indicators for valid drop targets
- Smooth animations and transitions

### 3. List Reordering
- Reorder list items by dragging
- Visual feedback showing drag position
- Automatic list updates on drop
- Support for complex list items

### 4. Dashboard Customization
- Customize dashboard layout with drag and drop
- Add/remove widgets from dashboard
- Organize widgets in different zones
- Save and restore custom layouts

## Components

### FileDropZone

A component for file upload via drag and drop.

```tsx
import { FileDropZone } from '@/components/dragdrop';

<FileDropZone
  onFileDrop={(files) => console.log('Files dropped:', files)}
  accept={['.pdf', '.jpg', '.png', 'image/*']}
  maxSize={5 * 1024 * 1024} // 5MB
  maxFiles={5}
/>
```

**Props:**
- `onFileDrop`: Callback function when files are dropped
- `accept`: Array of accepted file types (MIME types or extensions)
- `maxSize`: Maximum file size in bytes
- `maxFiles`: Maximum number of files allowed
- `validateFile`: Custom validation function
- `disabled`: Disable the drop zone

### DraggableList

A component for creating lists with drag-to-reorder functionality.

```tsx
import { DraggableList } from '@/components/dragdrop';

<DraggableList
  items={items}
  onReorder={(newItems) => setItems(newItems)}
  getId={(item) => item.id}
  renderItem={(item) => <div>{item.name}</div>}
/>
```

**Props:**
- `items`: Array of items to display
- `onReorder`: Callback when items are reordered
- `getId`: Function to get unique ID from item
- `renderItem`: Function to render each item
- `showDragHandle`: Show/hide drag handle (default: true)

### DraggableCard

A component that can be dragged and dropped.

```tsx
import { DraggableCard } from '@/components/dragdrop';

<DraggableCard
  id="card-1"
  type="widget"
  data={cardData}
  onDragStart={(item) => console.log('Drag started:', item)}
>
  <Card title="My Card">Content</Card>
</DraggableCard>
```

**Props:**
- `id`: Unique identifier for the card
- `type`: Type of draggable item (for validation)
- `data`: Data associated with the card
- `onDragStart`: Callback when drag starts
- `onDragEnd`: Callback when drag ends
- `disabled`: Disable dragging

### DropZone

A component that accepts draggable items.

```tsx
import { DropZone } from '@/components/dragdrop';

<DropZone
  id="zone-1"
  accepts={['widget', 'card']}
  onDrop={(item) => console.log('Item dropped:', item)}
  validateDrop={(item) => item.data.isValid}
>
  {/* Drop zone content */}
</DropZone>
```

**Props:**
- `id`: Unique identifier for the drop zone
- `accepts`: Array of accepted item types
- `onDrop`: Callback when item is dropped
- `validateDrop`: Custom validation function
- `emptyMessage`: Message shown when zone is empty
- `disabled`: Disable the drop zone

### DashboardCustomizer

A complete dashboard customization system.

```tsx
import { DashboardCustomizer } from '@/components/dragdrop';

<DashboardCustomizer
  availableWidgets={widgets}
  initialLayout={layout}
  onLayoutChange={(newLayout) => saveLayout(newLayout)}
  zones={['main', 'sidebar', 'footer']}
/>
```

**Props:**
- `availableWidgets`: Array of available widgets
- `initialLayout`: Initial dashboard layout
- `onLayoutChange`: Callback when layout changes
- `zones`: Array of zone identifiers

## Hooks

### useDragAndDrop

Core hook for drag and drop functionality.

```tsx
import { useDragAndDrop } from '@/hooks/useDragAndDrop';

const {
  draggedItem,
  dropTarget,
  isDragging,
  handleDragStart,
  handleDragEnd,
  handleDragOver,
  handleDragLeave,
  handleDrop,
} = useDragAndDrop({
  onDragStart: (item) => console.log('Drag started'),
  onDrop: (item, dropZone) => console.log('Dropped'),
  validateDrop: (item, dropZone) => true,
});
```

### useFileDragAndDrop

Hook specifically for file drag and drop.

```tsx
import { useFileDragAndDrop } from '@/hooks/useDragAndDrop';

const {
  isDraggingOver,
  error,
  handleDragOver,
  handleDragLeave,
  handleDrop,
} = useFileDragAndDrop({
  onFileDrop: (files) => uploadFiles(files),
  accept: ['.pdf', 'image/*'],
  maxSize: 5 * 1024 * 1024,
  maxFiles: 10,
});
```

### useListReorder

Hook for list reordering functionality.

```tsx
import { useListReorder } from '@/hooks/useDragAndDrop';

const {
  draggedIndex,
  dropIndex,
  handleDragStart,
  handleDragOver,
  handleDrop,
  handleDragEnd,
} = useListReorder({
  items: listItems,
  onReorder: (newItems) => setListItems(newItems),
  getId: (item) => item.id,
});
```

## Validation

### File Validation

The file drop zone supports multiple validation methods:

```tsx
<FileDropZone
  // Accept specific file types
  accept={['.pdf', '.docx', 'image/*', 'application/pdf']}
  
  // Limit file size
  maxSize={10 * 1024 * 1024} // 10MB
  
  // Limit number of files
  maxFiles={5}
  
  // Custom validation
  validateFile={(file) => {
    // Custom validation logic
    return file.name.includes('report');
  }}
/>
```

### Drop Validation

Validate drops before accepting them:

```tsx
<DropZone
  accepts={['widget']}
  validateDrop={(item) => {
    // Only accept items with specific properties
    return item.data.category === 'analytics';
  }}
  onDrop={(item) => handleDrop(item)}
/>
```

## Visual Feedback

The drag and drop system provides visual feedback:

1. **Drag Start**: Item becomes semi-transparent
2. **Drag Over**: Drop zone highlights
3. **Valid Drop**: Green border on drop zone
4. **Invalid Drop**: Red border or no highlight
5. **Drop Complete**: Animation and state update

## Accessibility

The drag and drop system includes accessibility features:

- Keyboard navigation support (planned)
- Screen reader announcements (planned)
- Focus management
- ARIA labels and roles
- Alternative input methods

## Best Practices

### 1. Provide Clear Visual Feedback

```tsx
<DropZone
  id="zone-1"
  accepts={['widget']}
  onDrop={handleDrop}
  emptyMessage="Drop widgets here to add them to your dashboard"
>
  {items.length === 0 && (
    <div className="empty-state">
      <i className="pi pi-inbox"></i>
      <p>No items yet</p>
    </div>
  )}
</DropZone>
```

### 2. Validate Before Processing

```tsx
const handleFileDrop = (files: File[]) => {
  // Additional validation
  const validFiles = files.filter(file => {
    if (file.size > MAX_SIZE) {
      showError(`File ${file.name} is too large`);
      return false;
    }
    return true;
  });
  
  // Process valid files
  uploadFiles(validFiles);
};
```

### 3. Handle Errors Gracefully

```tsx
<FileDropZone
  onFileDrop={(files) => {
    try {
      processFiles(files);
    } catch (error) {
      showError('Failed to process files');
    }
  }}
  validateFile={(file) => {
    if (!isValidFileType(file)) {
      showError(`Invalid file type: ${file.name}`);
      return false;
    }
    return true;
  }}
/>
```

### 4. Persist User Preferences

```tsx
const DashboardWithPersistence = () => {
  const [layout, setLayout] = useState(() => {
    // Load from localStorage
    const saved = localStorage.getItem('dashboardLayout');
    return saved ? JSON.parse(saved) : defaultLayout;
  });

  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
    // Save to localStorage
    localStorage.setItem('dashboardLayout', JSON.stringify(newLayout));
  };

  return (
    <DashboardCustomizer
      initialLayout={layout}
      onLayoutChange={handleLayoutChange}
      {...otherProps}
    />
  );
};
```

## Examples

See `frontend/src/examples/DragAndDropDemo.tsx` for complete working examples of all drag and drop functionality.

## Browser Support

The drag and drop system uses the HTML5 Drag and Drop API and is supported in:
- Chrome 4+
- Firefox 3.5+
- Safari 3.1+
- Edge (all versions)
- Opera 12+

## Performance Considerations

1. **Large Lists**: Use virtualization for lists with many items
2. **Heavy Components**: Optimize render performance of draggable items
3. **Validation**: Keep validation logic lightweight
4. **State Updates**: Batch state updates when possible

## Troubleshooting

### Drag Not Working

- Ensure `draggable` attribute is set to `true`
- Check that drag handlers are properly attached
- Verify no CSS is preventing pointer events

### Drop Not Triggering

- Ensure `onDragOver` prevents default behavior
- Check that drop zone accepts the item type
- Verify validation logic is not rejecting drops

### Visual Feedback Not Showing

- Check CSS classes are properly applied
- Verify state updates are triggering re-renders
- Ensure CSS transitions are not disabled

## Future Enhancements

- Touch device support
- Keyboard navigation
- Undo/redo functionality
- Drag preview customization
- Multi-select drag and drop
- Nested drag and drop
