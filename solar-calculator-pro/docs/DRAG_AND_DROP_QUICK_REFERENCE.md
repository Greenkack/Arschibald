# Drag and Drop Quick Reference

## Quick Start

```tsx
import {
  FileDropZone,
  DraggableList,
  DraggableCard,
  DropZone,
  DashboardCustomizer,
} from '@/components/dragdrop';
```

## File Upload

```tsx
<FileDropZone
  onFileDrop={(files) => handleFiles(files)}
  accept={['.pdf', 'image/*']}
  maxSize={5 * 1024 * 1024}
  maxFiles={5}
/>
```

## List Reordering

```tsx
<DraggableList
  items={items}
  onReorder={setItems}
  getId={(item) => item.id}
  renderItem={(item) => <div>{item.name}</div>}
/>
```

## Component Dragging

```tsx
// Draggable Item
<DraggableCard id="1" type="widget" data={data}>
  <Card>Content</Card>
</DraggableCard>

// Drop Target
<DropZone
  id="zone-1"
  accepts={['widget']}
  onDrop={(item) => handleDrop(item)}
/>
```

## Dashboard Customization

```tsx
<DashboardCustomizer
  availableWidgets={widgets}
  initialLayout={layout}
  onLayoutChange={setLayout}
  zones={['main', 'sidebar']}
/>
```

## Common Patterns

### File Upload with Validation

```tsx
<FileDropZone
  onFileDrop={(files) => uploadFiles(files)}
  accept={['.pdf', '.docx']}
  maxSize={10 * 1024 * 1024}
  validateFile={(file) => file.name.includes('report')}
/>
```

### Sortable List

```tsx
const [items, setItems] = useState([...]);

<DraggableList
  items={items}
  onReorder={setItems}
  getId={(item) => item.id}
  renderItem={(item) => (
    <div>
      <h3>{item.title}</h3>
      <p>{item.description}</p>
    </div>
  )}
/>
```

### Drag Between Zones

```tsx
const [zone1, setZone1] = useState([...]);
const [zone2, setZone2] = useState([...]);

<DropZone
  id="zone1"
  accepts={['card']}
  onDrop={(item) => {
    setZone2(prev => prev.filter(i => i.id !== item.id));
    setZone1(prev => [...prev, item.data]);
  }}
>
  {zone1.map(item => (
    <DraggableCard key={item.id} id={item.id} type="card" data={item}>
      <Card>{item.content}</Card>
    </DraggableCard>
  ))}
</DropZone>
```

## Hooks

### useDragAndDrop

```tsx
const {
  draggedItem,
  isDragging,
  handleDragStart,
  handleDrop,
} = useDragAndDrop({
  onDrop: (item, zone) => console.log('Dropped'),
});
```

### useFileDragAndDrop

```tsx
const {
  isDraggingOver,
  error,
  handleDragOver,
  handleDrop,
} = useFileDragAndDrop({
  onFileDrop: (files) => upload(files),
  maxSize: 5 * 1024 * 1024,
});
```

### useListReorder

```tsx
const {
  draggedIndex,
  handleDragStart,
  handleDrop,
} = useListReorder({
  items,
  onReorder: setItems,
  getId: (item) => item.id,
});
```

## Validation

```tsx
// File validation
<FileDropZone
  accept={['.pdf']}
  maxSize={5 * 1024 * 1024}
  maxFiles={10}
  validateFile={(file) => file.size > 0}
/>

// Drop validation
<DropZone
  accepts={['widget']}
  validateDrop={(item) => item.data.isValid}
  onDrop={handleDrop}
/>
```

## Styling

```css
/* Custom drop zone styles */
.file-drop-zone {
  border: 2px dashed #ccc;
  padding: 2rem;
}

.file-drop-zone.dragging-over {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

/* Custom draggable item styles */
.draggable-list-item {
  cursor: move;
}

.draggable-list-item.dragging {
  opacity: 0.5;
}
```

## Error Handling

```tsx
const [error, setError] = useState<string | null>(null);

<FileDropZone
  onFileDrop={(files) => {
    try {
      processFiles(files);
      setError(null);
    } catch (err) {
      setError('Failed to process files');
    }
  }}
/>

{error && <Message severity="error" text={error} />}
```

## Persistence

```tsx
// Save layout
const handleLayoutChange = (layout) => {
  localStorage.setItem('layout', JSON.stringify(layout));
  setLayout(layout);
};

// Load layout
const [layout, setLayout] = useState(() => {
  const saved = localStorage.getItem('layout');
  return saved ? JSON.parse(saved) : defaultLayout;
});
```

## Common Issues

### Drag not working
- Check `draggable={true}` is set
- Verify drag handlers are attached
- Ensure no CSS blocking pointer events

### Drop not triggering
- Call `e.preventDefault()` in `onDragOver`
- Check item type matches `accepts` array
- Verify validation logic

### No visual feedback
- Check CSS classes are applied
- Verify state updates trigger re-renders
- Ensure transitions are enabled

## Requirements

- React 18+
- PrimeReact 10+
- Modern browser with HTML5 Drag and Drop API support

## See Also

- [Complete Guide](./DRAG_AND_DROP_GUIDE.md)
- [Demo Examples](../frontend/src/examples/DragAndDropDemo.tsx)
- [API Documentation](./API_DOCUMENTATION.md)
